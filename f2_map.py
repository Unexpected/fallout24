class Map: 
	def __init__(self, json_data): 
		self.data = json_data
		self.levels = self.data["levels"]
		self.tiles = self.levels[0]["tiles"]
		self.spatials = self.levels[0]["spatials"]
		self.objects = self.levels[0]["objects"]
		self.floor = self.tiles["floor"]
		self.roof = self.tiles["roof"]
		
	def __str__(self): 
		return "name: %s, mapID: %s, version: %s" % (self.data["name"], self.data["mapID"], self.data["version"])
	
	def get_floor_tiles(self): 
		# return tuples: (x, y, tile)
		# do not return grid000 tiles ?? 
		floor_tiles = []
		TILES_SIZE = 100
		for y in range(TILES_SIZE): 
			for x in range(TILES_SIZE): 
				tile = self.floor[y][x]
				if tile != "grid000":
					floor_tiles.append((x, y, tile))
		return floor_tiles
		
