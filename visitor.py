import csv
from datetime import datetime

class Visitor(object):
	def __init__(self):
		self.firstvisit_datetime = []
		#self.lastvisit_datetime = 0
		#self.total_visits = 0

		self.face_id_idx = 0
		self.visitor_visit_count = 0
		self.face_ids = []
		self.lastvisit_datetime = []
		self.total_visits = []		

		self.readcsv = None
		self.empty_csv = True
		self.opencsv = None
		self.writecsv = None

		try:
			with open('visitors.csv', mode='a+', newline='') as visitcsv:
				print("visitors.csv existed")
		except Exception as e:
			print(e)


	def load_csv(self):

		# Using "w" you won't be able to read the file.
		# https://stackoverflow.com/questions/44901806/python-error-message-io-unsupportedoperation-not-readable
		with open('visitors.csv', mode='r', newline='') as visitcsv:
			self.readcsv = csv.reader(visitcsv, delimiter=',')
			self.rowcnt = 0
			for row in self.readcsv:
				if(self.rowcnt == 0):
					pass
				elif(self.rowcnt >= 1):
					self.face_id_idx = int(row[0])
					self.face_ids.append(row[0])  # list face_id
					self.firstvisit_datetime.append(row[1])  # list visit_datetime
					self.lastvisit_datetime.append(row[2])			# list face_id					
					self.total_visits.append(row[3]) # face_match_distance 							
				
				self.rowcnt += 1

		#self.opencsv = open('visitors.csv', mode='w', newline='')
		#self.writecsv = csv.writer(self.opencsv, delimiter=',')
		
		# empty csv, add title
		#if self.rowcnt == 0:
		#	self.writecsv.writerow(['face_id','firstvisit_datetime','lastvisit_datetime','total_visits'])
		#	print('#1 vsitor csv header write')

		return self.lastvisit_datetime,  self.total_visits

	def register_visitor(self):
		self.face_id_idx += 1
		self.visitor_visit_count = 1

		self.face_ids.append(str(self.face_id_idx))
		self.firstvisit_datetime.append(datetime.now())			
		self.lastvisit_datetime.append(datetime.now())	
		self.total_visits.append("1")
		return self.face_id_idx, self.lastvisit_datetime,  self.total_visits


	def csv_dump(self, visit_counts):
		self.total_visits = visit_counts
		try:		
			with open('visitors.csv', mode='w', newline='') as opencsv:
				self.writecsv = csv.writer(opencsv, delimiter=',')
				self.writecsv.writerow(['face_id','firstvisit_datetime','lastvisit_datetime','total_visits'])
				
				i = 0
				while i <= len(self.face_ids) : 
					print('#8 visit csv_dump - loop')
					print(self.face_ids[i], '-', self.firstvisit_datetime[i], '-', self.lastvisit_datetime[i], '-', visit_counts[i])
					self.writecsv.writerow([self.face_ids[i], self.firstvisit_datetime[i], self.lastvisit_datetime[i], visit_counts[i]])
					i += 1

		except Exception as e:
			print(e)