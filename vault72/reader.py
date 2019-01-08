import sys, traceback, struct
import record
import json

# global paths/flags
ESP_FILE = None
OPT1 = False
OPT2 = False

def log(msg): 
	print(msg, file=sys.stderr)

def main():
	global ESP_FILE, PROTOTYPES_FILE
	
	if len(sys.argv) < 3:
		print("USAGE:", sys.argv[0], "ESP_FILE", "PROTOTYPES_FILE")
		return

	ESP_FILE = sys.argv[1]
	PROTOTYPES_FILE = sys.argv[2]
	
	try:
		with open(ESP_FILE, "rb") as esp_file:
			#builder = record.RecordBuilder(esp_file)
			#builder.read()
			records = []
			while esp_file.read(1): 
				esp_file.seek(-1, 1)
				r = record.Record()
				r.read(esp_file)
				records.append(r)
			
		with open(PROTOTYPES_FILE, "r") as proto_file: 
			prototypes = json.loads(proto_file.read())
		
		for r in records: 
			r.analyze_data(prototypes)
			print(r.detail)
			
	except Exception:
		traceback.print_exc()

if __name__ == "__main__":
	main()