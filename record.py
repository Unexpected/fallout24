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
	try: 
		return data.read(int(data_type))
	except: 
		pass
	
	if data_type == "Z": # Z String
		data_size = readU16(data)
		return data.read(data_size).decode("utf-8")[:-1]
	elif data_type == "z": # Z bytes
		data_size = readU16(data)
		return data.read(data_size)
	elif data_type == "O": 
		data_size = readU16(data) 
		return struct.unpack("i", data.read(4))[0] # form ID - always Int32
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
		#print(f.read(68))
		#f.seek(-68, 1)
		self.type = readString(f, 4)
		self.data_size = readU32(f)
		if self.type == "GRUP": 
			self.label = f.read(4)
			self.group_type = readU32(f)
			if self.group_type == 0: 
				self.label = self.label.decode("utf-8")
			elif self.group_type == 2 or self.group_type == 3 or self.group_type == 6: 
				self.label = int(struct.unpack("I", self.label)[0])
				
		else: 
			self.flags = readU32(f)
			self.id = readU32(f)
		self.rev = readU32(f)
		self.version = readU16(f)
		self.unknown = readU16(f)
		return 24
	
	def read_data(self, f): 
		if self.type == "GRUP": 
			self.raw_data = f.read(self.data_size - 24)
			return self.data_size - 24
		elif self.type == "NPC_" or self.type == "CELL": 
			# TODO - is compressed ?? - how many bytes to read ??? 
			self.compressed_data_size = readU32(f) 
			print("%s - read %d bytes of compressed data" % (self.type, self.compressed_data_size))
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
		#print("read %s - %d bytes" % (self.type, self.data_size))
		return read_bytes

	def analyze_data(self, prototypes, lvl): 
		if self.type == "GRUP": 
			self.analyzeGRUP(prototypes, lvl)
			return

		print("%sanalyze data for %s" % ("\t"*lvl, self.type))
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
				print("REMAINING DATA not in prototype: ")
				print(data.read(24))
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
					sr[field] = readFromBytes(data_type, data)
			else: 
				(field, data_type) = sub_record[1].split("|")
				#print("try to read %s %s" % (field, data_type))
				#print(data.read(8))
				#data.seek(-8, 1)
				sr[field] = readFromBytes(data_type, data)
				
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
			print("%sread a sub group record %s of size %d" % ("\t"*lvl, r.type, r.data_size))
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

