import record, plugin

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

# global paths/flags
F2_DATA_DIR = None
OPT1 = False
OPT2 = False

def main():
	global F2_DATA_DIR, RAW_INPUT_DIR

	plugin = Plugin()
	
	plugin.buildTES4(RAW_INPUT_DIR)

	# for each map ?
	plugin.buildNPC_(F2_DATA_DIR, RAW_INPUT_DIR)
	plugin.buildCELL(F2_DATA_DIR, RAW_INPUT_DIR)
	
	plugin.write("f2gen.esp")

if __name__ == "__main__":
	main()