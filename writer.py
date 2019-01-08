import record, plugin

# global paths/flags
F2_DATA_DIR = None
OPT1 = False
OPT2 = False

def main():
	global F2_DATA_DIR, OPT1, OPT2

	plugin = record.Plugin()
	plugin.fill()
	plugin.write("f2gen.esp")

if __name__ == "__main__":
	main()