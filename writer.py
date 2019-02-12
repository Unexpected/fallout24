import sys, record, json, f2_map, grup, struct, zlib, math, os
from plugin import Plugin
from grup import GRUP

MAP_SIZE_FACTOR = 128

OBJECTS = dict()
OBJECTS["F2CovenantGenericM01"] = 33560401
OBJECTS["F2CovenantGenericF01"] = 33560403
OBJECTS["TreeElmForest01Institute"] = 2011464
OBJECTS["TreeMapleInstitute05Green"] = 2011474
OBJECTS["LS_WaterPumpStatic"] = 2284588
OBJECTS["BldWoodBSmFlrOnly01"] = 486400
OBJECTS["BldWoodBSmFlrOnly02"] = 486401
OBJECTS["BldWoodBSmFlrOnly04"] = 486403
OBJECTS["BldWoodBSmFlrOnly09"] = 486408
OBJECTS["TreeSapling03"] = 1742810
OBJECTS["TreeMaplePreWar04Gr"] = 398918
OBJECTS["FloraWildCornStalk01"] = 1851412
OBJECTS["CampFireMed01_Off"] = 396627
OBJECTS["CinderBlockSquare01"] = 7680
OBJECTS["RWResPost01"] = 252692
OBJECTS["BldBrickSmFlrPlatQuarter01"] = 575511

OBJECTS["BldWoodBBGWall01"] = 486165

TILES = dict()
TILES["edg5003"] = "BldWoodBSmFlrOnly01"
TILES["edg5000"] = "BldWoodBSmFlrOnly01"
TILES["edg5002"] = "BldWoodBSmFlrOnly01"
TILES["edg5004"] = "BldWoodBSmFlrOnly01"
TILES["edg5005"] = "BldWoodBSmFlrOnly01"
TILES["edg5007"] = "BldWoodBSmFlrOnly01"
TILES["edg5003"] = "BldWoodBSmFlrOnly01"
TILES["edg5006"] = "BldWoodBSmFlrOnly02"
TILES["edg5001"] = "BldWoodBSmFlrOnly04"

# global paths/flags
F2_DATA_DIR = None
RAW_INPUT_DIR = None
OPT1 = False
OPT2 = False

def get_map_files(map_name, F2_DATA_DIR): 
	map_file_path = "%s/maps/%s.json" % (F2_DATA_DIR, map_name)
	map_images_file_path = "%s/maps/%s.images.json" % (F2_DATA_DIR, map_name)

	with open(map_file_path, "r") as map_file: 
		map = f2_map.Map(json.loads(map_file.read()))
	
	with open(map_images_file_path, "r") as map_images_file: 
		map_images = json.loads(map_images_file.read())
		
	return map, map_images

BASE_ID = 33558500
def get_id(): 
	global BASE_ID
	BASE_ID += 1
	return BASE_ID
	
def get_raw_header(type, data_size, flags, id = None): 
	raw_header = type.encode("utf-8") # type 
	raw_header += struct.pack("I", data_size) # data_size
	raw_header += struct.pack("I", flags) # flags
	raw_header += struct.pack("I", id if id else get_id()) # id
	raw_header += struct.pack("I", 0) # rev
	raw_header += struct.pack("H", 131) # version
	raw_header += struct.pack("H", 0) # rev2
	return raw_header
	
def get_tes4_header(data_size): 
	raw_header = "TES4".encode("utf-8") # type 
	raw_header += struct.pack("I", data_size) # data_size
	raw_header += struct.pack("I", 0) # flags
	raw_header += struct.pack("I", 0) # id
	raw_header += struct.pack("I", 0) # rev
	raw_header += struct.pack("H", 131) # version
	raw_header += struct.pack("H", 0) # rev2
	return raw_header

	
def get_refr_raw_data(map_name, floor_tiles, objs, v_walls, h_walls, entrances): 
	raw_data = b''
	for (x, y, tile) in floor_tiles: 
		if tile in TILES: 
			edid = OBJECTS[TILES[tile]]
		else: 
			edid = OBJECTS["BldWoodBSmFlrOnly09"]
		with open("raw/REFR/%s" % edid, "rb") as raw_base_file: 
			refr = raw_base_file.read()
		
		# REFR is : 
		# NAME(4) + EDID(2+4) + DATA(4)+data_size(2) + x(4) + y(4) + z(4) + rx(4) + ry(4) + rz(4)
		refr = refr[:16] + struct.pack("f", x*MAP_SIZE_FACTOR) + struct.pack("f", y*MAP_SIZE_FACTOR) + refr[24:]

		refr_header = get_raw_header("REFR", len(refr), 0)
		raw_data += (refr_header + refr)
		#print("%d/%d %s" % (x, y, refr))

	for (x, y, dir) in entrances: 
		edid = "coc_%s" % (map_name)
		eid += 1
		# REFR is : 
		# EDID / NAME / DATA 
		refr = "EDID".encode("utf-8") + struct.pack("H", len(edid)) + edid.encode("utf-8")
		refr += "NAME".encode("utf-8") + struct.pack("H", 4) + struct.pack("I", 50)
		refr += "DATA".encode("utf-8") + struct.pack("H", 24) + struct.pack("f", x*MAP_SIZE_FACTOR) + struct.pack("f", y*MAP_SIZE_FACTOR) + struct.pack("f", 0) + struct.pack("f", 0) + struct.pack("f", 0) + struct.pack("f", 0)

		refr_header = get_raw_header("REFR", len(refr), 0)
		raw_data += (refr_header + refr)

		break  # Only one COC for each cell ?? 

	eid = 0
	for (x, y, dir) in entrances: 
		edid = "Entrance_%d" % (eid)
		eid += 1
		# REFR is : 
		# EDID / NAME / DATA 
		refr = "EDID".encode("utf-8") + struct.pack("H", len(edid)) + edid.encode("utf-8")
		refr += "NAME".encode("utf-8") + struct.pack("H", 4) + struct.pack("I", 126327)
		refr += "DATA".encode("utf-8") + struct.pack("H", 24) + struct.pack("f", x*MAP_SIZE_FACTOR) + struct.pack("f", y*MAP_SIZE_FACTOR) + struct.pack("f", 0) + struct.pack("f", 0) + struct.pack("f", 0) + struct.pack("f", 0)

		refr_header = get_raw_header("REFR", len(refr), 0)
		raw_data += (refr_header + refr)

	types_to_do = dict()
	for (x, y, type, object) in objs: 
		z = 0
		if type == "walls": 
			edid = OBJECTS["CinderBlockSquare01"]
		#elif object == "block": 
		#	if type == "misc": 
		#		pass
		#		# edid = OBJECTS["RWResPost01"]
		#	else: 
		#		edid = OBJECTS["CinderBlockSquare01"]
		elif "exit" in object: 
			edid = OBJECTS["BldBrickSmFlrPlatQuarter01"]
			z = 5
		elif "tree" in object: 
			edid = OBJECTS["TreeMaplePreWar04Gr"]
		elif "weed" in object: 
			edid = OBJECTS["TreeSapling03"]
		elif "corn" in object: 
			edid = OBJECTS["FloraWildCornStalk01"]
		elif "woodfire" in object: 
			edid = OBJECTS["CampFireMed01_Off"]
		else: 
			if object not in types_to_do: 
				types_to_do[object] = 0
			types_to_do[object] += 1
			continue
			
		with open("raw/REFR/2011474", "rb") as raw_base_file: 
			refr = raw_base_file.read()
		
		# REFR is : 
		# NAME(4) + EDID(2+4) + DATA(4)+data_size(2) + x(4) + y(4) + z(4) + rx(4) + ry(4) + rz(4)
		refr = refr[:6] + struct.pack("I", edid) + refr[10:16] + struct.pack("f", x*MAP_SIZE_FACTOR) + struct.pack("f", y*MAP_SIZE_FACTOR) + struct.pack("f", z) + refr[28:]
		refr_header = get_raw_header("REFR", len(refr), 0)
		raw_data += (refr_header + refr)
		#print("%d/%d %s" % (x, y, refr))
	
	#print(types_to_do)
	#print(walls)
	for wall in v_walls: 
		for (x, y, type, wall_name) in wall:
			with open("raw/REFR/2011474", "rb") as raw_base_file: 
				refr = raw_base_file.read()
			
			edid = OBJECTS["BldWoodBBGWall01"]
			y = 0.5 * y
			if x % 2 != 0: 
				y -= 0.25
			x = 0.5 * x

			#print("wall at %f/%f" % (x, y))
			# REFR is : 
			# NAME(4) + EDID(2+4) + XSCL(2+4) + DATA(4)+data_size(2) + x(4) + y(4) + z(4) + rx(4) + ry(4) + rz(4)
			refr = refr[:6] + struct.pack("I", edid)
			refr += "XSCL".encode("utf-8") + struct.pack("H", 4) + struct.pack("f", 0.25)
			refr += "DATA".encode("utf-8") + struct.pack("H", 24) + struct.pack("f", x*MAP_SIZE_FACTOR + 30) + struct.pack("f", y*MAP_SIZE_FACTOR) + struct.pack("f", 0) + struct.pack("f", 0) + struct.pack("f", 0) + struct.pack("f", 0)
			refr_header = get_raw_header("REFR", len(refr), 0)
			raw_data += (refr_header + refr)

			with open("raw/REFR/2011474", "rb") as raw_base_file: 
				refr = raw_base_file.read()
			
			refr = refr[:6] + struct.pack("I", edid)
			refr += "XSCL".encode("utf-8") + struct.pack("H", 4) + struct.pack("f", 0.25)
			refr += "DATA".encode("utf-8") + struct.pack("H", 24) + struct.pack("f", x*MAP_SIZE_FACTOR - 30) + struct.pack("f", y*MAP_SIZE_FACTOR) + struct.pack("f", 0) + struct.pack("f", 0) + struct.pack("f", 0) + struct.pack("f", math.radians(180))
			refr_header = get_raw_header("REFR", len(refr), 0)
			raw_data += (refr_header + refr)


	for wall in h_walls: 
		for (x, y, type, wall_name) in wall:
			with open("raw/REFR/2011474", "rb") as raw_base_file: 
				refr = raw_base_file.read()
			
			edid = OBJECTS["BldWoodBBGWall01"]

			# placement is different for walls because of the "zigzag" line of hex tiles
			y = 0.5 * (y-1)
			#if x % 2 != 0: 
			#	y -= 0.5
			x = 0.5 * x


			#print("wall at %f/%f" % (x, y))
			# REFR is : 
			# NAME(4) + EDID(2+4) + XSCL(2+4) + DATA(4)+data_size(2) + x(4) + y(4) + z(4) + rx(4) + ry(4) + rz(4)
			refr = refr[:6] + struct.pack("I", edid)
			refr += "XSCL".encode("utf-8") + struct.pack("H", 4) + struct.pack("f", 0.25)
			refr += "DATA".encode("utf-8") + struct.pack("H", 24) + struct.pack("f", x*MAP_SIZE_FACTOR) + struct.pack("f", y*MAP_SIZE_FACTOR) + struct.pack("f", 0) + struct.pack("f", 0) + struct.pack("f", 0) + struct.pack("f", math.radians(90))
			refr_header = get_raw_header("REFR", len(refr), 0)
			raw_data += (refr_header + refr)

			with open("raw/REFR/2011474", "rb") as raw_base_file: 
				refr = raw_base_file.read()
			
			refr = refr[:6] + struct.pack("I", edid)
			refr += "XSCL".encode("utf-8") + struct.pack("H", 4) + struct.pack("f", 0.25)
			refr += "DATA".encode("utf-8") + struct.pack("H", 24) + struct.pack("f", x*MAP_SIZE_FACTOR) + struct.pack("f", y*MAP_SIZE_FACTOR+64) + struct.pack("f", 0) + struct.pack("f", 0) + struct.pack("f", 0) + struct.pack("f", math.radians(270))
			refr_header = get_raw_header("REFR", len(refr), 0)
			raw_data += (refr_header + refr)

	return raw_data

def get_cell_raw_data(form_id, edid): 
	raw_data = b''
	with open("raw/CELL/arroyoVillage", "rb") as raw_base_file: 
		raw_base_file.read(4)
		edid_size = struct.unpack("H", raw_base_file.read(2))[0]
		raw_base_file.read(edid_size)
		
		raw_base_file.read(4)
		full_size = struct.unpack("H", raw_base_file.read(2))[0]
		raw_base_file.read(full_size)
		
		cell_data = raw_base_file.read()

	raw_data += "EDID".encode("utf-8")
	raw_data += struct.pack("H", len(edid))
	raw_data += edid.encode("utf-8")
	
	full = edid + " marker"
	raw_data += "FULL".encode("utf-8")
	raw_data += struct.pack("H", len(full))
	raw_data += full.encode("utf-8")
	
	raw_data += cell_data
	return raw_data
	
	
def get_raw_grup_header(data_size, label, group_type): 
	raw_header = "GRUP".encode("utf-8") # type 
	raw_header += struct.pack("I", data_size + 24) # data_size of grup includes headers
	if group_type == 0: 
		raw_header += label.encode("utf-8")
	elif group_type in [2, 3, 6, 9]: 
		raw_header += struct.pack("I", label) # long, block number
	else: 
		print("GRUP type not managed: %d" % group_type) 
		raise Exception("GRUP type not managed: %d" % group_type) # form ID
	raw_header += struct.pack("I", group_type) # group_type
	raw_header += struct.pack("I", 0) # rev
	raw_header += struct.pack("H", 131) # version
	raw_header += struct.pack("H", 0) # rev2
	return raw_header

def get_map_cell_sub_block(map, number, level): 
	floor_tiles = map.get_floor_tiles(level)
	objs = map.get_objects(level)
	v_walls, h_walls = map.get_walls(level)
	entrances = map.get_entrances(level)
	map_name = map.name[:-4] + "_" + str(level)

	#x_min, y_min, width, height = map.get_map_size()

	cell_id = get_id()
	# refr_data									analyze data for REFR                                               
	refr_data = get_refr_raw_data(map_name, floor_tiles, objs, v_walls, h_walls, entrances)

	# temp_grup								analyze GRUP of size 2280 - label b'\x99\x0f\x00\x02' - type 9              
	temp_grup_header = get_raw_grup_header(len(refr_data), cell_id, 9)
	temp_grup = temp_grup_header + refr_data

	#									 CELL children of CELL ID 33558425                                                  
	# cell_children_grup			analyze GRUP of size 2304 - label 33558425 - type 6                                 
	cell_children_grup_header = get_raw_grup_header(len(temp_grup), cell_id, 6)
	cell_children = cell_children_grup_header + temp_grup

	# cell_record					analyze data for CELL                                                               
	cell_record_data = get_cell_raw_data(cell_id, map_name)
	compressed_flag = int('0x00040000', 16)
	compressed_data = struct.pack("I", len(cell_record_data)) + zlib.compress(cell_record_data)

	cell_record_header = get_raw_header("CELL", len(compressed_data), compressed_flag, cell_id)
	cell_record = cell_record_header + compressed_data

	cell_sub_block_header = get_raw_grup_header(len(cell_record) + len(cell_children), number, 3)
	cell_sub_block = cell_sub_block_header + cell_record + cell_children
	return cell_sub_block


def main():
	#global F2_DATA_DIR, RAW_INPUT_DIR

	if len(sys.argv) < 3:
		print("USAGE:", sys.argv[0], "F2_DATA_DIR", "RAW_INPUT_DIR")
		return

	F2_DATA_DIR = sys.argv[1]
	RAW_INPUT_DIR = sys.argv[2]
	
	p = Plugin()
	
	#p.init(RAW_INPUT_DIR)
	#p.build_TES4()

	with open("%s/TES4" % RAW_INPUT_DIR, "rb") as tes4_file:
		tes4_raw_data = tes4_file.read()
	tes4_raw_header = get_tes4_header(len(tes4_raw_data))
	p.TES4 = (tes4_raw_header + tes4_raw_data)
	
	maps = dict()

	for map_file in os.listdir("%s/maps" % F2_DATA_DIR):
		if "images.json" in map_file: 
			continue
		with open("%s/maps/%s" % (F2_DATA_DIR, map_file), "r") as map_file: 
			map = f2_map.Map(json.loads(map_file.read()))
			if map.map_id < 0: 
				continue
			maps[map.map_id] = map

	for map in maps.values(): 
		exits = map.get_exits()
		for (map_id, pos, map_level, direction) in exits: 
			x = pos % 200
			y = pos // 200
			y = 0.5 * y
			if x % 2 != 0: 
				y -= 0.25
			x = 0.5 * x
			if not map_level in maps[map_id].entrances: 
				maps[map_id].entrances[map_level] = set()
			maps[map_id].entrances[map_level].add((x, y, direction))

	for map in maps.values(): 
		print("map %d, entrances: %s" % (map.map_id, map.entrances))
	
	sub_blocks = b''
	number = 0
	for map in maps.values():
		for level in range(len(map.levels)):
			sub_blocks += get_map_cell_sub_block(map, number, level)
			number += 1

	cell_block_header = get_raw_grup_header(len(sub_blocks), 3, 2)
	cell_block = cell_block_header + sub_blocks
	
	#print(len(cell_block))
	top_grup_header = get_raw_grup_header(len(cell_block), "CELL", 0)
	#print(top_grup_header)
	top_grup = top_grup_header + cell_block
	
	p.GRUPs.append(top_grup)
	
	p.write("f2gen.esp")
	
	# for each map ?
	#plugin.buildNPC_(F2_DATA_DIR, RAW_INPUT_DIR)
	#plugin.buildCELL(F2_DATA_DIR, RAW_INPUT_DIR)
	
	#plugin.write("f2gen.esp")

if __name__ == "__main__":
	main()