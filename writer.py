import sys, record, json, f2_map, grup, struct
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
	
def get_raw_header(type, data_size): 
	raw_header = type.encode("utf-8") # type 
	raw_header += struct.pack("I", data_size) # data_size
	raw_header += struct.pack("I", 0) # flags
	raw_header += struct.pack("I", get_id()) # id
	raw_header += struct.pack("I", 0) # rev
	raw_header += struct.pack("H", 131) # version
	raw_header += struct.pack("H", 0) # rev2
	return raw_header
	
def get_refr_raw_data(floor_tiles): 
	raw_data = b''
	for (x, y, tile) in floor_tiles: 
		if tile in TILES: 
			edid = OBJECTS[TILES[tile]]
		else: 
			edid = OBJECTS["BldWoodBSmFlrOnly09"]
		with open("raw/REFR/%d" % edid, "rb") as raw_base_file: 
			refr = raw_base_file.read()
		
		# REFR is : 
		# NAME(4) + EDID(2+4) + DATA(4)+data_size(2) + x(4) + y(4) + z(4) + rx(4) + ry(4) + rz(4)
		refr = refr[:16] + struct.pack("f", x*256) + struct.pack("f", y*256) + refr[24:]
		refr_header = get_raw_header("REFR", len(refr))
		raw_data += (refr_header + refr)
		#print("%d/%d %s" % (x, y, refr))
	return raw_data

def main():
	#global F2_DATA_DIR, RAW_INPUT_DIR

	if len(sys.argv) < 3:
		print("USAGE:", sys.argv[0], "F2_DATA_DIR", "RAW_INPUT_DIR")
		return

	F2_DATA_DIR = sys.argv[1]
	RAW_INPUT_DIR = sys.argv[2]
	
	p = Plugin()
	
	p.init(RAW_INPUT_DIR)
	p.build_TES4()

	map, map_images = get_map_files("arvillag", F2_DATA_DIR)
	floor_tiles = map.get_floor_tiles()
	
	refr_data = get_refr_raw_data(floor_tiles)
	#print(refr_data)
	
			
	
	
	# for each map ?
	#plugin.buildNPC_(F2_DATA_DIR, RAW_INPUT_DIR)
	#plugin.buildCELL(F2_DATA_DIR, RAW_INPUT_DIR)
	
	#plugin.write("f2gen.esp")

if __name__ == "__main__":
	main()