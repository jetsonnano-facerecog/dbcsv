import face_recognition
import cv2
from datetime import datetime, timedelta
import numpy as np
import platform
import pickle
import csv
import time


#from visit import Visit
from visits import Visit
from visitor import Visitor

# Set this depending on your camera type:
# - True = Raspberry Pi 2.x camera module
# - False = USB webcam or other USB video input (like an HDMI capture device)
USING_RPI_CAMERA_MODULE = False

# Our list of known face encodings and a matching list of metadata about each face.
known_face_encodings = []
known_face_metadata = []
known_face_id = []
visit_face_match_distance = []
lastvisit_datetime = []
visitor_total_visits = []
visit_face_id = []


NEW_VISIT_TIMEOUT = 30*60 # if detected after 30 mins, consider as new visitpython

def save_known_faces():
    with open("known_faces.dat", "wb") as face_data_file:
        face_data = [known_face_id, known_face_encodings, known_face_metadata]
        pickle.dump(face_data, face_data_file)
        print("Known faces backed up to disk.")


def load_known_faces():
    global face_id, nown_face_encodings, known_face_metadata

    try:
        with open("known_faces.dat", "rb") as face_data_file:
            known_face_id, known_face_encodings, known_face_metadata = pickle.load(face_data_file)
            print("Known faces loaded from disk.")
            print("known_face_id ", known_face_id)
    except FileNotFoundError as e:
        print("No previous face data found - starting with a blank known face list.")
        pass


def get_jetson_gstreamer_source(capture_width=1280, capture_height=720, display_width=1280, display_height=720, framerate=60, flip_method=0):
    """
    Return an OpenCV-compatible video source description that uses gstreamer to capture video from the RPI camera on a Jetson Nano
    """
    return (
            f'nvarguscamerasrc ! video/x-raw(memory:NVMM), ' +
            f'width=(int){capture_width}, height=(int){capture_height}, ' +
            f'format=(string)NV12, framerate=(fraction){framerate}/1 ! ' +
            f'nvvidconv flip-method={flip_method} ! ' +
            f'video/x-raw, width=(int){display_width}, height=(int){display_height}, format=(string)BGRx ! ' +
            'videoconvert ! video/x-raw, format=(string)BGR ! appsink'
            )


def register_new_face(face_id, face_encoding, face_image):
    """
    Add a new person to our list of known faces
    """
    # Add the face encoding to the list of known faces
    known_face_encodings.append(face_encoding)
    # Add a matching dictionary entry to our metadata list.
    # We can use this to keep track of how many times a person has visited, when we last saw them, etc.
    known_face_metadata.append({
        "first_seen": datetime.now(),
        "first_seen_this_interaction": datetime.now(),
        "last_seen": datetime.now(),
        "seen_count": 1,
        "seen_frames": 1,
        "face_image": face_image,
        "face_id": face_id
    })

    known_face_id.append(face_id)




def lookup_known_face(face_encoding):
    """
    See if this is a face we already have in our face list
    """
    metadata = None
    face_distances = 0.0

    # If our known face list is empty, just return nothing since we can't possibly have seen this face.
    if len(known_face_encodings) == 0:
        return face_distances, metadata

    # Calculate the face distance between the unknown face and every face on in our known face list
    # This will return a floating point number between 0.0 and 1.0 for each known face. The smaller the number,
    # the more similar that face was to the unknown face.
    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

    # Get the known face that had the lowest distance (i.e. most similar) from the unknown face.
    best_match_index = np.argmin(face_distances)

    # If the face with the lowest distance had a distance under 0.6, we consider it a face match.
    # 0.6 comes from how the face recognition model was trained. It was trained to make sure pictures
    # of the same person always were less than 0.6 away from each other.
    # Here, we are loosening the threshold a little bit to 0.65 because it is unlikely that two very similar
    # people will come up to the door at the same time.
    if face_distances[best_match_index] < 0.65:
        # If we have a match, look up the metadata we've saved for it (like the first time we saw it, etc)
        metadata = known_face_metadata[best_match_index]

        # Update the metadata for the face so we can keep track of how recently we have seen this face.
        metadata["last_seen"] = datetime.now()
        metadata["seen_frames"] += 1

        # We'll also keep a total "seen count" that tracks how many times this person has come to the door.
        # But we can say that if we have seen this person within the last 5 minutes, it is still the same
        # visit, not a new visit. But if they go away for awhile and come back, that is a new visit.
        if datetime.now() - metadata["first_seen_this_interaction"] > timedelta(minutes=NEW_VISIT_TIMEOUT):
            metadata["first_seen_this_interaction"] = datetime.now()
            metadata["seen_count"] += 1


    return face_distances[best_match_index] , metadata


def main_loop():


    # Get access to the webcam. The method is different depending on if you are using a Raspberry Pi camera or USB input.
    if USING_RPI_CAMERA_MODULE:
        # Accessing the camera with OpenCV on a Jetson Nano requires gstreamer with a custom gstreamer source string
        video_capture = cv2.VideoCapture(get_jetson_gstreamer_source(), cv2.CAP_GSTREAMER)
    else:
        # Accessing the camera with OpenCV on a laptop just requires passing in the number of the webcam (usually 0)
        # Note: You can pass in a filename instead if you want to process a video file instead of a live camera stream
        video_capture = cv2.VideoCapture("ayah2.mp4")

    # Track how long since we last saved a copy of our known faces to disk as a backup.
    number_of_faces_since_save = 0
    cv2.namedWindow('Video', cv2. WINDOW_NORMAL)
    cv2.resizeWindow('Video', (480,270))
    start_timer = time.time()
    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()
        if ret == False:
            print("No video input")
            break

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Find all the face locations and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        # Loop through each detected face and see if it is one we have seen before
        # If so, we'll give it a label that we'll draw on top of the video.
        face_labels = []
        for face_location, face_encoding in zip(face_locations, face_encodings):
            # See if this face is in our list of known faces.
            face_distances, metadata = lookup_known_face(face_encoding)
            

            # If we found the face, label the face with some useful information.
            if metadata is not None:
                time_at_door = datetime.now() - metadata['first_seen_this_interaction']
                face_label = f"At door {int(time_at_door.total_seconds())}s"
                #visitor.record_revisit_to_csv(visit.get_faceid(),metadata['first_seen_this_interaction'], metadata['seen_count'])
                visit_face_match_distance[curr_visit_id] = face_distances  # update face_id value of currebt visit_id
                visit_face_id[curr_visit_id] = metadata['face_id']

                #print("visitor_total_visits : ", visitor_total_visits)
                #print("lastvisit_datetime : ", lastvisit_datetime)                
                #print("metadata['face_id'] : ", metadata['face_id'])

                visitor_total_visits[metadata['face_id']-1] = metadata['seen_count']
                lastvisit_datetime[metadata['face_id']-1] = datetime.now()

            # If this is a brand new face, add it to our list of known faces
            else:
                face_label = "New visitor!"

                #visit.record_newvisit_to_csv(face_distance)

                # Grab the image of the the face from the current frame of video
                top, right, bottom, left = face_location
                face_image = small_frame[top:bottom, left:right]
                face_image = cv2.resize(face_image, (150, 150))

                visitor_face_id, lastvisit_datetime, visitor_total_visits = visitor.register_visitor()
                print("visitor_face_id ", visitor_face_id)
                register_new_face(visitor_face_id, face_encoding, face_image)

                # Add the new face to our known face data
                visit_face_id, visit_face_match_distance = visit.update_visit_class(visitor_face_id) # at first visit, face distance = -1                

                # save image each visitor to visit_id.jpg
                cv2.imwrite('id{}.jpg'.format(visitor_face_id) , face_image)



            face_labels.append(face_label)
            #visit.update_csv(visit.get_faceid(), face_distances) # face_distance valonly occured at 2nd,3rd,... vist
        

        # Draw a box around each face and label each face
        for (top, right, bottom, left), face_label in zip(face_locations, face_labels):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            cv2.putText(frame, face_label, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

        # Display recent visitor images
        number_of_recent_visitors = 0
        for metadata in known_face_metadata:
            # If we have seen this person in the last minute, draw their image
            if datetime.now() - metadata["last_seen"] < timedelta(seconds=10) and metadata["seen_frames"] > 5:
                # Draw the known face image
                x_position = number_of_recent_visitors * 150
                frame[30:180, x_position:x_position + 150] = metadata["face_image"]
                number_of_recent_visitors += 1

                # Label the image with how many times they have visited
                visits = metadata['seen_count']
                visit_label = f"{visits} visits"
                if visits == 1:
                    visit_label = "First visit"
                cv2.putText(frame, visit_label, (x_position + 10, 170), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

        if number_of_recent_visitors > 0:
            cv2.putText(frame, "Visitors at Door", (5, 18), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)



        # Display the final frame of video with boxes drawn around each detected fames

        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            visit.csv_dump(visit_face_id,visit_face_match_distance)
            visitor.csv_dump(visitor_total_visits)
            save_known_faces()
            break

        if time.time() - start_timer > 5 :
            print("Loop 3 sec")
            if len(face_locations) > 0 :
                visit.csv_dump(visit_face_id, visit_face_match_distance)
                visitor.csv_dump(visitor_total_visits)
            start_timer = time.time()


        # We need to save our known faces back to disk every so often in case something crashes.
        if len(face_locations) > 0 and number_of_faces_since_save > 100:
            save_known_faces()
            number_of_faces_since_save = 0
        else:
            number_of_faces_since_save += 1

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    visit = Visit()
    visitor = Visitor()

    visit_datetime = []

    curr_visit_id, visit_face_id, visit_face_match_distance = visit.load_csv()
    print("curr_visit_id ", curr_visit_id)
    print("visit_face_id", visit_face_id)
    lastvisit_datetime, visitor_total_visits = visitor.load_csv()
    print("lastvisit_datetime ", lastvisit_datetime)
    print("visitor_total_visits", visitor_total_visits)

    load_known_faces()
    main_loop()
