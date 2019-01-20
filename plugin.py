import record


class Plugin(): 
	def __init__(self): 
		self.TES4 = None
		self.GRUPs = []

	def init(self, raw_data_dir): 
		self.raw_data_dir = raw_data_dir
		
	def build_TES4(self): 
		with open("%s/TES4" % self.raw_data_dir, "rb") as tes4_file:
			self.TES4 = tes4_file.read()
		
	def get_raw_data(): 
		raw = self.TES4
		for grup in self.GRUPs: 
			raw += grup
		return raw
	
	def write(self, target_file_path): 
		with open(target_file_path, 'wb') as plugin_file: 
			plugin_file.write(self.get_raw_data())

			
	