import zlib
from record import Record

class GRUP(Record): 
	def __init__(self): 
		self.headers = None
		
		self.data = None
	
	def init_type(self, type): 
		pass
	
	def build_raw(self): 
		self.raw_headers = self.build_raw_headers()
		
		self.raw_data = self.build_raw_data()
		if self.is_compressed(): 
			self.compressed_data += zlib.compress(self.raw_data)
	
	def get_raw_data(self): 
		self.build_raw()
		
		raw_data = self.raw_headers
		if self.is_compressed(): 
			raw_data += self.compressed_data
		else: 
			raw_data += self.raw_data
		
		return raw_data
