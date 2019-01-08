import struct, collections, zlib, io

# reading methods, parameter f is a file opened in binary mode
def read8(f):
	return struct.unpack("b", f.read(1))[0]

def readU8(f):
	return struct.unpack("B", f.read(1))[0]

def read16(f):
	return struct.unpack("h", f.read(2))[0]

def readU16(f):
	return struct.unpack("H", f.read(2))[0]

def read32(f):
	return struct.unpack("i", f.read(4))[0]

def readU32(f):
	return struct.unpack("I", f.read(4))[0]

def readU64(f):
	return struct.unpack("Q", f.read(8))[0]

def readULong(f):
	return struct.unpack("L", f.read(4))[0]
	
def readFloat(f):
	return struct.unpack("f", f.read(4))[0]

def readString(f, size):
	return f.read(size).decode("utf-8")

def readFromBytes(data_type, data): 
	if data_type == "Z": 
		data_size = readU16(data)
		return readString(data, data_size)[:-1]
	elif data_type == "b" or data_type == "B": 
		return struct.unpack(data_type, data.read(1))[0]
	elif data_type == "h" or data_type == "H": 
		return struct.unpack(data_type, data.read(2))[0]
	elif data_type == "i" or data_type == "I" or data_type == "L" or data_type == "f": 
		return struct.unpack(data_type, data.read(4))[0]
	elif data_type == "Q": 
		return struct.unpack(data_type, data.read(8))[0]
		
def isiterable(value): 
	return isinstance(value, collections.Iterable) and not isinstance(value, str)
	
class Record(): 
	def __init__(self):
		self.type = None
		self.detail = dict()

	def read_metainfo(self, f): 
		self.type = readString(f, 4)
		self.data_size = readU32(f)
		self.flags = readU32(f)
		self.id = readU32(f)
		self.rev = readU32(f)
		self.version = readU16(f)
		self.unknown = readU16(f)
	
	def read_data(self, f): 
		if self.type == "GRUP": 
			self.raw_data = f.read(self.data_size - 24)
		elif self.type == "NPC_": 
			# TODO - is compressed ??
			uncompressed_size = f.read(4)
			self.raw_data = zlib.decompress(f.read(self.data_size))
		else: 
			self.raw_data = f.read(self.data_size)
		
	def read(self, f): 
		self.read_metainfo(f)
		self.read_data(f)
		print("read %s - %d bytes" % (self.type, self.data_size))

	def analyze_data(self, prototypes): 
		if self.type == "GRUP": 
			self.analyzeGRUP(prototypes)
			return

		print("analyze data for %s" % self.type)
		sub_records = prototypes[self.type]
		print(sub_records)
		data = io.BytesIO(self.raw_data)
		
		index = 0
		# until there is no more data
		while data.read(1):
			data.seek(-1, 1)

			if index >= len(sub_records): 
				#print(self.detail)
				#print(data.read(20))
				#raise Exception("REMAINING DATA not in prototype")
				print("REMAINING DATA not in prototype")
				break
				
			sub_record = sub_records[index]
			type = readString(data, 4)
			if sub_record[0] != type: 
				# record not here, continue
				data.seek(-4, 1)
				index += 1
				continue

			sr = dict()
			sr["type"] = type
			# we've got the good sub_record
			if isiterable(sub_record[1]): 
				# complex struct
				for desc in sub_record[1]:
					(field, data_type) = desc.split("|")
					sr[field] = readFromBytes(data_type, data)
			else: 
				(field, data_type) = sub_record[1].split("|")
				print("try to read %s %s" % (field, data_type))
				print(data.read(8))
				data.seek(-8, 1)
				sr[field] = readFromBytes(data_type, data)
				
			if len(sub_record) > 2: 
				index -= int(sub_record[2])

			name = sr["type"]
			if name in self.detail:
				i = 0
				while (name + str(i)) in self.detail: 
					i += 1
				name = name + str(i)
			
			print(sr)
			self.detail[name] = sr
			
	def analyzeGRUP(self, prototypes): 
		
		sub_records = []
		b = io.BytesIO(self.raw_data)
		while b.read(1): 
			b.seek(-1, 1)
			r = Record()
			r.read(b)
			r.analyze_data(prototypes)
			sub_records.append(r)
		#print(prototypes)
		
	def check_type(self, f): 
		found_type = readString(f, 4)
		if self.type != found_type: 
			raise Exception("READ_RECORD_WRONG_TYPE", "expected: %s, found: %s" % (self.type, found_type))
	
	def read_record(self, record, f): 
		try: 
			record.read(f)
			return record
		except Exception: 
			if record.optional: 
				f.seek(-4, 1)
				return None
			else: 
				raise
	
	def read_new_record(self, f): 
		type = readString(f, 4)
		data_size = readU16(f)
		
		
	def pretty_print(self, tabs): 
		s = "\t" * tabs + "Record %s: \n" % self.type
		tabs += 1
		for k, v in self.__dict__.items():
			if isinstance(v, collections.Iterable) and not isinstance(v, str): 
				s += ("\t" * tabs + "%s= [\n" % k)
				for r in v: 
					if isinstance(r, tuple): 
						s += r[0].pretty_print(tabs + 1)
						s += r[1].pretty_print(tabs + 1)
					else: 
						s += r.pretty_print(tabs + 1)
				s += ("\t" * tabs + "]\n")
			elif isinstance(v, Record): 
				s += v.pretty_print(tabs)
			else: 
				s += ("\t" * tabs + "%s= %s\n" % (k, v))
		return s
	
	def __str__(self): 
		s = "Record %s: \n" % self.type
		for k, v in self.__dict__.items():
			s += ("%s= %s\n" % (k, v))
		return s

class StringRecord(Record): 
	def __init__(self, type, optional):
		self.type = type
		self.optional = optional
		self.data_size = 0
		self.data = None
	
	def read(self, f): 
		self.check_type(f)
		self.data_size = readU16(f)
		self.data = readString(f, self.data_size)
		return self
		
class GRUP(Record): 
	def __init__(self):
		self.type = "GRUP"
		self.optional = True
		self.groupSize = -1
		self.label = ""
		self.groupType = -1
		self.stamp = -1
		self.unknown = -1
		self.version = -1
		self.unknown2 = -1
		self.data = None
	
	def read(self, f): 
		self.check_type(f)
		self.groupSize = readU32(f)
		self.label = str(f.read(4))
		self.groupType = read32(f)
		self.stamp = readU16(f)
		self.unknown = readU16(f)
		self.version = readU16(f)
		self.unknown2 = readU16(f)
		self.data = None # uint8[groupSize-24]
		
		return self


class NPC_(Record): 
	def __init__(self):
		self.type = "NPC_"
		self.optional = True
		
	def read(self, f): 
		self.check_type(f)
		self.data_size = readU16(f)
		self.flags = readU32(f)
		self.id = readU32(f)
		self.rev = readU32(f)
		self.version = readU16(f)
		self.unknown = readU16(f)
		self.something = readU16(f)
		self.decomp_size = readU32(f)
		data = f.read(self.data_size-4)
		
		#print(f.read(4))
		
		#print(zlib.decompress(data))
		
		read_size = 0

		self.srEDID = self.EDID()
		self.srEDID = self.read_record(self.srEDID, f)
		# read_size += self.srEDID.data_size + 6		
		return self

	class EDID(StringRecord): 
		def __init__(self): 
			StringRecord.__init__(self, "EDID", True)
			
class CELL(Record): 
	def __init__(self):
		self.type = "CELL"
		self.optional = True
	
	def read(self, f): 
		self.check_type(f)
		self.data_size = readU16(f)
		self.flags = readU32(f)
		self.id = readU32(f)
		self.rev = readU32(f)
		self.version = readU16(f)
		self.unknown = readU16(f)
		self.something = readU16(f)
		self.decomp_size = readU32(f)
		data = f.read(self.data_size-4)
		
		print(zlib.decompress(data))
		
		return self
			
class RecordBuilder(): 
	def __init__(self, esp_file):
		self.file = esp_file
		
	def read(self): 
		record = TES4()
		r = record.read(self.file)
		print(r.pretty_print(0))
		
		record = GRUP()
		r = record.read(self.file)
		print(r.pretty_print(0))

		record = NPC_()
		r = record.read(self.file)
		print(r.pretty_print(0))

		record = NPC_()
		r = record.read(self.file)
		print(r.pretty_print(0))
		
		record = GRUP()
		r = record.read(self.file)
		print(r.pretty_print(0))
		
		record = GRUP()
		r = record.read(self.file)
		print(r.pretty_print(0))
		
		record = GRUP()
		r = record.read(self.file)
		print(r.pretty_print(0))
		
		record = CELL()
		r = record.read(self.file)
		print(r.pretty_print(0))

		record = GRUP()
		r = record.read(self.file)
		print(r.pretty_print(0))

		record = GRUP()
		r = record.read(self.file)
		print(r.pretty_print(0))
		
		print("next is %s" % self.file.read(4))
		
		
		
	def read_record(self, f): 
		module = __import__(module_name)
		class_ = getattr(module, type)
		r = class_()
		r.data_size = readU32(f)
		r.flags = record.readU32(f)
		r.id = readU32(f)
		r.rev = readU32(f)
		r.version = readU16(f)
		r.unknown = readU16(f)
		
		sub_records = r.get_sr_def()
	
	
		print("# HEDR	header	struct")
		# HEDR	header	struct
		r = esp_file.read(4)
		print(r)
		r = esp_file.read(2)
		print(r)
		# version	float	0.94 in most files; 1.7 in recent versions of Update.esm.
		r = record.readFloat(esp_file)
		print(r)

		# numRecords	int32	Number of records and groups (not including TES4 record itself).
		r = record.read32(esp_file)
		print(r)

		# nextObjectId	ulong	Next available object ID.
		r = record.readULong(esp_file)
		print(r)
		
		
		cname = esp_file.read(4)
		print(cname)
		author = esp_file.read(48)
		print(author)

