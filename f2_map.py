class Map: 
	def __init__(self, json_data): 
		self.data = json_data
		self.name = self.data["name"]
		self.map_id = self.data["mapID"]
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
	
	def get_objects(self): 
		# return tuples: (x, y, tile)
		# do not return grid000 tiles ?? 
		objs = []
		
		for object in self.objects: 
			x = int(object["position"]["x"])
			y = int(object["position"]["y"])
			y = 0.5 * y
			if x % 2 != 0: 
				y -= 0.25
			x = 0.5 * x
			objs.append((x, y, object["art"].split("/")[2]))
		return objs
	
	
	def get_map_size(self): 
		floor_tiles = self.get_floor_tiles()
		x_min = min([int(f[0]) for f in floor_tiles])
		y_min = min([int(f[1]) for f in floor_tiles])
		x_max = max([int(f[0]) for f in floor_tiles])
		y_max = max([int(f[1]) for f in floor_tiles])
		width = x_max - x_min
		height = y_max - y_min
		return x_min, y_min, width, height
