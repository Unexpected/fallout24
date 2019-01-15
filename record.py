import struct, collections, zlib, io

UINT_LENGTH = dict()
UINT_LENGTH[1] = "B"
UINT_LENGTH[2] = "H"
UINT_LENGTH[4] = "I"
UINT_LENGTH[8] = "Q"

VARIABLE_LENGTH_TYPES = { "O", "N", "X", "Z" }

def read_fixed_size(data_size, data_type, data): 
	""" This methods reads a fixed size from a byte stream and returns length of data read + data read formatted according to parameters 
	data_types: 
		"X": read byte array
		"W": read UTF-8 word 
		"Z": read UTF-8 string ending with \x00
		something else: return struct.unpack data with data_type used as parameter	
	"""
	if data_type == "X": 
		return data_size, data.read(data_size)
	elif data_type == "Z": 
		return data_size, data.read(data_size).decode("utf-8")
	return data_size, struct.unpack(data_type, data.read(data_size))[0]

def read_variable_size(data_type, data): 
	""" This method reads from a byte stream and returns length of data read + data read formatted according to parameters 
	data_types: 
		b / B: int8 / uint8 (1 byte)
		h / H: int16 / uint16 (2 bytes)
		i / I: int32 / uint32 (4 bytes)
		l / L / f: long / ULong / float (4 bytes each)
		Q: unsigned long long (8 bytes)
		O: Form ID with uint16 + int32
		N: Variable unsigned integer with uint16 as length + uint[length]
		Z: variable size string with uint16 as str_len + utf-8 string of size str_len
		X: variable size byte struct with uint16 as bytes_len + byte array of size bytes_len
		integer n: temp hack for weird structures - read and return n bytes
	"""
	
	try: 
		return int(data_type), data.read(int(data_type))
	except: 
		pass

	data_size = 0
	if data_type in VARIABLE_LENGTH_TYPES: 
		data_size = readU16(data)
		if data_type == "N": 
			data_type = UINT_LENGTH[data_size]
		elif data_type == "O": 
			data_type = "i"
			data_size = 4
	elif data_type == "b" or data_type == "B": 
		data_size = 1
	elif data_type == "h" or data_type == "H": 
		data_size = 2
	elif data_type == "i" or data_type == "I" or data_type == "L" or data_type == "f":
		data_size = 4
	elif data_type == "Q": 
		data_size = 8

	return read_fixed_size(data_size, data_type, data)

def read8(f):
	return read_fixed_size(1, "b", f)[1]

def readU8(f):
    return read_fixed_size(1, "B", f)[1]

def read16(f):
	return read_fixed_size(2, "h", f)[1]

def readU16(f):
	return read_fixed_size(2, "H", f)[1]

def read32(f):
	return read_fixed_size(4, "i", f)[1]

def readU32(f):
	return read_fixed_size(4, "I", f)[1]

def readString(f, size):
	return read_fixed_size(size, "Z", f)[1]
	
def isiterable(value): 
	return isinstance(value, collections.Iterable) and not isinstance(value, str)
	
class Record(): 
	def __init__(self):
		self.type = None
		self.detail = dict()

	def read_metainfo(self, f): 
		#print(f.read(68))
		#f.seek(-68, 1)
		read_size = 0
		self.type = readString(f, 4)
		read_size += 4
		self.data_size = readU32(f)
		read_size += 4
		
		if self.type == "GRUP": 
			self.label = f.read(4)
			read_size += 4
			self.group_type = readU32(f)
			read_size += 4
			if self.group_type == 0: 
				self.label = self.label.decode("utf-8")
			elif self.group_type == 2 or self.group_type == 3 or self.group_type == 6: 
				self.label = int(struct.unpack("I", self.label)[0])
				
		else: 
			self.flags = readU32(f)
			read_size += 4
			self.id = readU32(f)
			read_size += 4
		self.rev = readU32(f)
		read_size += 4
		self.version = readU16(f)
		read_size += 2
		self.unknown = readU16(f)
		read_size += 2
		return read_size
	
	def is_compressed(self): 
		compressed_flag = int('0x00040000', 16)
		return compressed_flag & self.flags
		
	def read_data(self, f): 
		if self.type == "GRUP": 
			self.raw_data = f.read(self.data_size - 24)
			return self.data_size - 24
		elif self.is_compressed(): 
			# Compresed flag: 0x00040000	Data is compressed
			# TODO - is compressed ?? - how many bytes to read ??? 
			self.compressed_data_size = readU32(f) 
			#print("%s - read %d bytes of compressed data" % (self.type, self.compressed_data_size))
			self.compressed_data = f.read(self.data_size - 4)
			self.raw_data = zlib.decompress(self.compressed_data)
			#print("end of compressed data")
			#print(self.compressed_data[-20:])
			return self.data_size - 4
		else: 
			self.raw_data = f.read(self.data_size)
			return self.data_size
		
	def read(self, f): 
		read_bytes = self.read_metainfo(f)
		read_bytes+= self.read_data(f)
		
		if self.type == "TES4": 
			f.seek(-read_bytes, 1)
			raw = f.read(read_bytes)
			with open("raw/TES4", "wb") as dump_file: 
				dump_file.write(raw)
		
		#print("read %s - %d bytes" % (self.type, self.data_size))
		return read_bytes

	def analyze_data(self, prototypes, lvl): 
		if self.type == "GRUP": 
			self.analyzeGRUP(prototypes, lvl)
			return

		#print("%sanalyze data for %s" % ("\t"*lvl, self.type))
		sub_records = prototypes[self.type]
		#print(sub_records)
		data = io.BytesIO(self.raw_data)
		
		index = 0
		# until there is no more data
		while data.read(1):
			data.seek(-1, 1)

			if index >= len(sub_records): 
				#print(self.detail)
				#
				#raise Exception("REMAINING DATA not in prototype")
				#print("REMAINING DATA not in prototype: ")
				#print(data.read(24))
				#print(self.raw_data)
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
					sr[field] = read_variable_size(data_type, data)[1]
			else: 
				(field, data_type) = sub_record[1].split("|")
				sr[field] = read_variable_size(data_type, data)[1]
				
			if len(sub_record) > 2: 
				index -= int(sub_record[2])

			name = sr["type"]
			if name in self.detail:
				i = 0
				while (name + str(i)) in self.detail: 
					i += 1
				name = name + str(i)
			
			#print("data analyzed: %s" % sr)
			self.detail[name] = sr
			
	def analyzeGRUP(self, prototypes, lvl): 
		sub_records = []
		
		print("%sanalyze GRUP of size %d - label %s - type %d" % ("\t"*lvl, self.data_size, self.label, self.group_type))
		if self.group_type == 0: 
			print("%s type #0 - Top group of %s" % ("\t"*lvl, self.label))
		elif self.group_type == 2: 
			print("%s type #2 - Interior cell block, block number %d" % ("\t"*lvl, self.label))
		elif self.group_type == 3: 
			print("%s type #3 - Interior cell sub-block, sub-block number %d" % ("\t"*lvl, self.label))
		elif self.group_type == 6:
			print("%s CELL children of CELL ID %d" % ("\t"*lvl, self.label))
		b = io.BytesIO(self.raw_data)
		read_bytes_len = 0
		while b.read(1): 
			b.seek(-1, 1)
			r = Record()
			read_bytes_len += r.read(b)
			#print("%sread a sub group record %s of size %d" % ("\t"*lvl, r.type, r.data_size))
			#print("%sbytes remaining: %d " % ("\t"*lvl, len(self.raw_data) - read_bytes_len))
			r.analyze_data(prototypes, lvl+1)
			sub_records.append(r)
		
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
					elif isinstance(r, Record): 
						s += r.pretty_print(tabs + 1)
					else: 
						s += ("\t" * (tabs+1) + "%s= %s\n" % (k, v))
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

