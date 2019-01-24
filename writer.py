import sys, record, json, f2_map, grup, struct, zlib
from plugin import Plugin
from grup import GRUP

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
	
def get_raw_header(type, data_size, flags): 
	raw_header = type.encode("utf-8") # type 
	raw_header += struct.pack("I", data_size) # data_size
	raw_header += struct.pack("I", flags) # flags
	raw_header += struct.pack("I", get_id()) # id
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

	
def get_refr_raw_data(floor_tiles, objs, x_min, y_min, width, height): 
	raw_data = b''
	for (x, y, tile) in floor_tiles: 
		real_x = (x - x_min) - width / 2
		real_y = (y - y_min) - height / 2
		if tile in TILES: 
			edid = OBJECTS[TILES[tile]]
		else: 
			edid = OBJECTS["BldWoodBSmFlrOnly09"]
		with open("raw/REFR/%s" % edid, "rb") as raw_base_file: 
			refr = raw_base_file.read()
		
		# REFR is : 
		# NAME(4) + EDID(2+4) + DATA(4)+data_size(2) + x(4) + y(4) + z(4) + rx(4) + ry(4) + rz(4)
		refr = refr[:16] + struct.pack("f", real_x*256) + struct.pack("f", real_y*256) + refr[24:]

		refr_header = get_raw_header("REFR", len(refr), 0)
		raw_data += (refr_header + refr)
		#print("%d/%d %s" % (x, y, refr))
	
	types_to_do = dict()
	for (x, y, object) in objs: 
		if object == "block": 
			continue
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
			
		real_x = (x - x_min) - width / 2
		real_y = (y - y_min) - height / 2
		
		with open("raw/REFR/2011474", "rb") as raw_base_file: 
			refr = raw_base_file.read()
		
		# REFR is : 
		# NAME(4) + EDID(2+4) + DATA(4)+data_size(2) + x(4) + y(4) + z(4) + rx(4) + ry(4) + rz(4)
		refr = refr[:6] + struct.pack("I", edid) + refr[10:16] + struct.pack("f", real_x*256) + struct.pack("f", real_y*256) + refr[24:]
		refr_header = get_raw_header("REFR", len(refr), 0)
		raw_data += (refr_header + refr)
		#print("%d/%d %s" % (x, y, refr))
	
	print(types_to_do)
	
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
	
	map, map_images = get_map_files("arvillag", F2_DATA_DIR)
	floor_tiles = map.get_floor_tiles()
	objs = map.get_objects()
	x_min, y_min, width, height = map.get_map_size()
	print("%d, %d, %d, %d" % (x_min, y_min, width, height))
	#print(refr_data)

	# struct of the grup tree, in reverse order
	# 
	# refr_data									analyze data for REFR                                               
	# refr_data									analyze data for REFR                                               
	# refr_data									analyze data for REFR                                               
	#
	# temp_grup								analyze GRUP of size 2280 - label b'\x99\x0f\x00\x02' - type 9              
	#									 CELL children of CELL ID 33558425                                                  
	# cell_children_grup			analyze GRUP of size 2304 - label 33558425 - type 6                                 
	#
	# cell_record					analyze data for CELL                                                               
	#
	# cell_grup					 type #3 - Interior cell sub-block, sub-block number 9                                      
	#							analyze GRUP of size 2541 - label 9 - type 3                                                
	#						 type #2 - Interior cell block, block number 3                                                      
	#						analyze GRUP of size 2565 - label 3 - type 2                                                        
	#		 			type #0 - Top group of CELL                                                                                
	#					analyze GRUP of size 2882 - label CELL - type 0                                                             

	cell_id = get_id()
	# refr_data									analyze data for REFR                                               
	refr_data = get_refr_raw_data(floor_tiles, objs, x_min, y_min, width, height)

	# temp_grup								analyze GRUP of size 2280 - label b'\x99\x0f\x00\x02' - type 9              
	temp_grup_header = get_raw_grup_header(len(refr_data), cell_id, 9)
	temp_grup = temp_grup_header + refr_data

	#									 CELL children of CELL ID 33558425                                                  
	# cell_children_grup			analyze GRUP of size 2304 - label 33558425 - type 6                                 
	cell_children_grup_header = get_raw_grup_header(len(temp_grup), cell_id, 6)
	cell_children = cell_children_grup_header + temp_grup

	# cell_record					analyze data for CELL                                                               
	cell_record_data = get_cell_raw_data(cell_id, map.name)
	compressed_flag = int('0x00040000', 16)
	compressed_data = struct.pack("I", len(cell_record_data)) + zlib.compress(cell_record_data)

	cell_record_header = get_raw_header("CELL", len(compressed_data), compressed_flag)
	cell_record = cell_record_header + compressed_data
	print(cell_record_header)
	print(compressed_data)
	
	cell_sub_block_header = get_raw_grup_header(len(cell_record) + len(cell_children), 9, 3)
	cell_sub_block = cell_sub_block_header + cell_record + cell_children
	
	cell_block_header = get_raw_grup_header(len(cell_sub_block), 3, 2)
	cell_block = cell_block_header + cell_sub_block
	
	print(len(cell_block))
	top_grup_header = get_raw_grup_header(len(cell_block), "CELL", 0)
	print(top_grup_header)
	top_grup = top_grup_header + cell_block
	
	p.GRUPs.append(top_grup)
	
	p.write("f2gen.esp")
	
	# for each map ?
	#plugin.buildNPC_(F2_DATA_DIR, RAW_INPUT_DIR)
	#plugin.buildCELL(F2_DATA_DIR, RAW_INPUT_DIR)
	
	#plugin.write("f2gen.esp")

if __name__ == "__main__":
	main()