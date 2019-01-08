class Plugin(): 
	def __init__(self): 
		self.rTES4 = TES4()
		self.records = []
		
	def fill(self): 
		self.rTES4.fill()
		
	def write(self, target_file_path): 
		plugin_file = open(target_file_path, 'wb')
		
		self.rTES4.write(plugin_file)
		for r in self.records: 
			r.write(plugin_file)

		plugin_file.close()
	