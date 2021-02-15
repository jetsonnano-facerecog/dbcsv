

# Face Recognition

This repo is modified from : https://github.com/ageitgey/face_recognition/blob/master/examples/facerec_from_webcam_faster.py
main repo is https://github.com/ageitgey/face_recognition
Medium article https://medium.com/@ageitgey/build-a-face-recognition-system-for-60-with-the-new-nvidia-jetson-nano-2gb-and-python-46edbddd7264

## Installation

## Requirements

  * Python 3.3+ or Python 2.7
  * macOS or Linux (Windows not officially supported, but might work)

## Installing on an Nvidia Jetson Nano board

 * [Jetson Nano installation instructions](https://medium.com/@ageitgey/build-a-hardware-based-face-recognition-system-for-150-with-the-nvidia-jetson-nano-and-python-a25cb8c891fd)
   * Please follow the instructions in the article carefully. There is current a bug in the CUDA libraries on the Jetson Nano that will cause this library to fail silently if you don't follow the instructions in the article to comment out a line in dlib and recompile it.

### Installing Required Python Libraries
To build our face recognition system, we need to install several Python libraries. While the Jetson Nano has a lot of great stuff pre-installed, there are some odd omissions. For example, OpenCV is installed with Python bindings, but pip and numpy aren’t installed and those are required to do anything with OpenCV. Let’s fix that.
From the Jetson Nano desktop, open up a Terminal window and run the following commands. Any time it asks for your password, type in the same password that you entered when you created your user account:

```bash
sudo apt-get update
sudo apt-get install python3-pip cmake libopenblas-dev liblapack-dev libjpeg-dev
```
First, we are updating apt, which is the standard Linux software installation tool that we’ll use to install everything else. Next, we are installing some basic libraries with apt that we will need later to compile numpy and dlib.

### Jetson Nano 2GB
Before we go any further, we need to create a swapfile. The Jetson Nano only has 4GB of RAM which won’t be enough to compile dlib. To work around this, we’ll set up a swapfile which lets us use disk space as extra RAM. Luckily, there is an easy way to set up a swapfile on the Jetson Nano. Just run these two commands:
```bash
git clone https://github.com/JetsonHacksNano/installSwapfile
./installSwapfile/installSwapfile.sh
```
At this point, you need to reboot the system to make sure the swapfile is running. If you skip this, the next step will fail. You can reboot from the menu at the top right of the desktop.

### Install dlib
When you are logged back in, open up a fresh Terminal window and we can continue. First, let’s install numpy, a Python library that is used for matrix math calculations:
```bash
pip3 install numpy
```
This command will take 15 minutes since it has to compile numpy from scratch. Just wait until it finishes and don’t get worried it seems to freeze for a while.
Now we are ready to install dlib, a deep learning library created by Davis King that does the heavy lifting for the face_recognition library.
However, there is currently a bug in Nvidia’s own CUDA libraries for the Jetson Nano that keeps it from working correctly. To work around the bug, we’ll have to download dlib, edit a line of code, and re-compile it. But don’t worry, it’s no big deal.
In Terminal, run these commands:
```bash
wget http://dlib.net/files/dlib-19.17.tar.bz2 
tar jxvf dlib-19.17.tar.bz2
cd dlib-19.17
```

That will download and uncompress the source code for dlib. Before we compile it, we need to comment out a line. Run this command:
```bash
gedit dlib/cuda/cudnn_dlibapi.cpp
```

This will open up the file that we need to edit in a text editor. Search the file for the following line of code (which should be line 854):
```
forward_algo = forward_best_algo;

And comment it out by adding two slashes in front of it, so it looks like this:

//forward_algo = forward_best_algo;
```

Now save the file, close the editor, and go back to the Terminal window. Next, run these commands to compile and install dlib:
```bash
sudo python3 setup.py install
```
This will take around 30–60 minutes to finish and your Jetson Nano might get hot, but just let it run.
Finally, we need to install the face_recognition Python library. Do that with this command:
```bash
sudo pip3 install face_recognition
```
Now your Jetson Nano is ready to do face recognition with full CUDA GPU acceleration.
