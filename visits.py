import csv
from datetime import datetime
import pickle

class Visit(object):
	def __init__(self):
		self.curr_visit_id = 0
		self.cur_visit_datetime = None
		self.curr_face_id = 99
		self.face_match_distance = 0.0

		self.visit_ids = []
		self.visit_datetime = []
		self.face_id = []
		self.face_match_distance = []

		try:
			with open('visits.csv', mode='a+', newline='') as visitcsv:
				print("visits.csv existed")
		except Exception as e:
			print(e)

	def load_csv(self):
		#visit_datetime = []
		#face_id = []
		#face_match_distance = []

		# Using "w" you won't be able to read the file.
		# https://stackoverflow.com/questions/44901806/python-error-message-io-unsupportedoperation-not-readable
		with open('visits.csv', mode='r', newline='') as visitcsv:
			self.readcsv = csv.reader(visitcsv, delimiter=',')
			self.rowcnt = 0
			print("#1 row in self.readcsv")
			for row in self.readcsv:
				print("#2 row in self.readcsv")
				if(self.rowcnt == 0):
					pass
				elif(self.rowcnt >= 1):
					self.curr_visit_id = int(row[0])
					self.visit_ids.append(row[0])
					self.visit_datetime.append(row[1])  # list visit_datetime
					self.face_id.append(row[2])			# list face_id					
					self.face_match_distance.append(row[3]) # face_match_distance 							
				
				self.rowcnt += 1

		#self.opencsv = open('visits.csv', mode='w', newline='') 
		#self.writecsv = csv.writer(self.opencsv, delimiter=',')
		
		# empty csv, add title
		#if self.rowcnt == 0:
			##with open('visits.csv', mode='w+', newline='') as opencsv:
			#self.writecsv.writerow(['visit_id','visit_datetime','face_id','face_match_distance'])
			#print('#1- visit csv header write')

		return self.curr_visit_id, self.face_id,  self.face_match_distance

	def get_visitid(self):
		return self.curr_visit_id
	def set_visitid(self, visit_id):
		self.curr_visit_id = visit_id
	
	def csv_isEmpty(self):
		return self.empty_csv

	def update_visit_class(self, visitor_face_id):
		self.cur_visit_datetime = datetime.now()
		self.curr_visit_id += 1
		self.curr_face_id = visitor_face_id
		self.visit_ids.append(self.curr_visit_id)
		self.face_id.append(visitor_face_id)
		self.visit_datetime.append(datetime.now())			
		self.face_match_distance.append(0.0)	
		return self.face_id,  self.face_match_distance

	def csv_dump(self, face_id, face_match_distance):
		self.face_match_distance = face_match_distance

		try:		
			with open('visits.csv', mode='w', newline='') as opencsv:
				self.writecsv = csv.writer(opencsv, delimiter=',')
				self.writecsv.writerow(['visit_id','visit_datetime','face_id','face_match_distance'])

				i = 0
				while i <= self.curr_visit_id : 
					print('#4 visitor csv dump ')
					print(self.face_id[i], '-', self.visit_datetime[i], '-', self.face_id[i], '-', face_match_distance[i])
					self.writecsv.writerow([self.face_id[i], self.visit_datetime[i], self.face_id[i], face_match_distance[i]])
					i += 1

		except Exception as e:
			print(e)

