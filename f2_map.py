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
		x_min, y_min, x_max, y_max = self.get_map_bounds()
		# return tuples: (x, y, tile)
		# do not return grid000 tiles ?? 
		floor_tiles = []
		TILES_SIZE = 100
		for y in range(TILES_SIZE): 
			for x in range(TILES_SIZE): 
				if x < x_min - 2 or x > x_max + 2 or y < y_min - 2 or y > y_max + 2: 
					continue
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
			type = object["art"].split("/")[1]
			obj_name = object["art"].split("/")[2]
			y = 0.5 * y
			if x % 2 != 0: 
				y -= 0.25
			x = 0.5 * x
			objs.append((x, y, type, obj_name))
		return objs
	
	def get_walls(self): 
		wall_objects = dict()
		for object in self.objects: 
			type = object["art"].split("/")[1]
			obj_name = object["art"].split("/")[2]
			if type == "walls" or obj_name == "block" and type != "misc":
				x = int(object["position"]["x"])
				y = int(object["position"]["y"])
				wall_objects[x + 200*y] = (x, y, type, obj_name)

		real_walls = self.get_vertical_walls(wall_objects)
		
		v_walls = []
		for real_wall in real_walls: 
			#wall_str = ""
			wall = []
			for wall_piece_id in real_wall: 
				wall_object = wall_objects[wall_piece_id]
				#wall_str += "%d/%d - %s " % (wall_object[0], wall_object[1], wall_object[3])
				wall.append(wall_object)
			
			for wall_piece_id in real_wall[1:-1]: 
				del wall_objects[wall_piece_id]

			# print(real_walls)
			v_walls.append(wall)

		real_walls = self.get_horizontal_walls(wall_objects)
		h_walls = []
		for real_wall in real_walls: 
			#wall_str = ""
			wall = []
			for wall_piece_id in real_wall: 
				wall_object = wall_objects[wall_piece_id]
				#wall_str += "%d/%d - %s " % (wall_object[0], wall_object[1], wall_object[3])
				wall.append(wall_object)
				del wall_objects[wall_piece_id]
			# print(real_walls)
			h_walls.append(wall)
		
		return v_walls, h_walls			

	def get_vertical_walls(self, wall_objects): 
		vertical_walls = []
		vertical_pieces_done = set()
		for wall_piece_id in wall_objects.keys(): 
			if not wall_piece_id in vertical_pieces_done: 
				if wall_piece_id - 200 in wall_objects or wall_piece_id + 200 in wall_objects: 
					wall_sequence = set()
					wall_sequence.add(wall_piece_id)
					wid = wall_piece_id
					while wid - 200 in wall_objects: 
						wid -= 200
						wall_sequence.add(wid)
						vertical_pieces_done.add(wid)
					wid = wall_piece_id
					while wid + 200 in wall_objects: 
						wid += 200
						wall_sequence.add(wid)
						vertical_pieces_done.add(wid)

					vertical_walls.append(wall_sequence)
				vertical_pieces_done.add(wall_piece_id)

		real_walls = []
		for vertical_wall in sorted(vertical_walls): 
			wall = 0
			for wall_piece_id in sorted(list(vertical_wall)): 
				if wall_objects[wall_piece_id][3] != "block": 
					wall += 1
					if wall >= 2:
						real_walls.append(sorted(list(vertical_wall)))
						break

		return real_walls


	def get_horizontal_walls(self, wall_objects): 
		horizontal_sequences = []
		horizontal_pieces_done = set()
		for wall_piece_id in wall_objects.keys(): 
			# "horizontal" lines are zigzags on hexagons
			# from the start, it could zigzag on an upper hexagon, or a lower hexagon. We need to check both sequences
			if not wall_piece_id in horizontal_pieces_done: 
				if wall_piece_id - 1 in wall_objects or wall_piece_id + 1 in wall_objects: 
					wall_sequence = set()
					wall_sequence.add(wall_piece_id)
					wid = wall_piece_id
					while wid - 1 in wall_objects: 
						wid -= 1
						wall_sequence.add(wid)
						horizontal_pieces_done.add(wid)
					wid = wall_piece_id
					while wid + 1 in wall_objects: 
						wid += 1
						wall_sequence.add(wid)
						horizontal_pieces_done.add(wid)

					horizontal_sequences.append(wall_sequence)
				horizontal_pieces_done.add(wall_piece_id)

		real_walls = []
		for h_wall in sorted(horizontal_sequences): 
			wall = 0
			for wall_piece_id in h_wall: 
				if wall_objects[wall_piece_id][3] != "block": 
					wall += 1
					if wall >= 2:
						real_walls.append(h_wall)
						break
		
		for real_wall in real_walls: 
			wall_str = ""
			for wall_piece_id in real_wall: 
				wall_object = wall_objects[wall_piece_id]
				wall_str += "%d/%d - %s " % (wall_object[0], wall_object[1], wall_object[3])
			#print(wall_str)

		return real_walls


	def get_map_bounds(self): 
		x_min = min([int(o[0]) for o in self.get_objects()])
		y_min = min([int(o[1]) for o in self.get_objects()])
		x_max = max([int(o[0]) for o in self.get_objects()])
		y_max = max([int(o[1]) for o in self.get_objects()])
		return x_min, y_min, x_max, y_max

	
	def get_map_size(self): 
		x_min = min([int(o[0]) for o in self.get_objects() if o[2] == "misc" and o[3] == "block"])
		y_min = min([int(o[1]) for o in self.get_objects() if o[2] == "misc" and o[3] == "block"])
		x_max = max([int(o[0]) for o in self.get_objects() if o[2] == "misc" and o[3] == "block"])
		y_max = max([int(o[1]) for o in self.get_objects() if o[2] == "misc" and o[3] == "block"])
		print("%d, %d, %d, %d" % (x_min, y_min, x_max, y_max))
		
		x_min = min([int(o[0]) for o in self.get_objects()])
		y_min = min([int(o[1]) for o in self.get_objects()])
		x_max = max([int(o[0]) for o in self.get_objects()])
		y_max = max([int(o[1]) for o in self.get_objects()])
		width = x_max - x_min
		height = y_max - y_min
		print("%d, %d, %d, %d" % (x_min, y_min, x_max, y_max))

		
		return x_min, y_min, width, height
