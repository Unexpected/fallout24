class Plugin(): 
	def __init__(self): 
		self.TES4 = None
		self.GRUPs = []
	
	def get_raw_data(): 
		raw = self.TES4
		for grup in self.GRUPs: 
			raw += grup
		return raw
	
	def write(self, target_file_path): 
		with open(target_file_path, 'wb') as plugin_file: 
			plugin_file.write(self.get_raw_data())

			
	