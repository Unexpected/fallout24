class TES4(Record):
	def __init__(self):
		self.type = "TES4"
		self.optional = False
		self.srHEDR = None
		self.srCNAM = None
		self.srSNAM = None
		self.srMAST_DATA = None
	
	def fill(self): 
		self.flags = 0
		self.id = 0
		self.rev = 0
		self.version = 131
		self.unknown = 0
		self.data_size = 105 #to be computed
		
		self.srHEDR = self.HEDR()
		self.srHEDR.data_size = 12
		self.srHEDR.version = 0.94
		self.srHEDR.numRecords = 48
		self.srHEDR.nextObjectId = 5977

		self.srCNAM = self.CNAM()
		self.srCNAM.data_size = 8
		self.srCNAM.data = "DEFAULT"
		
		self.srMAST_DATA = []
		m1 = self.MAST()
		m1.data_size = 13
		m1.data = "Fallout4.esm"
		d1 = self.DATA()
		d1.data_size = 8
		d1.fileSize = 0
		self.srMAST_DATA.append((m1, d1))
		
		m2 = self.MAST()
		m2.data_size = 10
		m2.data = "F2ref.esm"
		d2 = self.DATA()
		d2.data_size = 8
		d2.fileSize = 0
		self.srMAST_DATA.append((m2, d2))      
		
		self.srINTV = self.INTV()
		self.srINTV.data_size = 4
		self.srINTV.unknown = 1
		
		
		
	def read(self, f): 
		self.check_type(f)
		self.data_size = readU32(f)
		self.flags = readU32(f)
		self.id = readU32(f)
		self.rev = readU32(f)
		self.version = readU16(f)
		self.unknown = readU16(f)
		read_size = 0

		self.srHEDR = self.HEDR()
		self.srHEDR = self.read_record(self.srHEDR, f)
		read_size += self.srHEDR.data_size + 6
		
		self.srCNAM = self.CNAM()
		self.srCNAM = self.read_record(self.srCNAM, f)
		read_size += self.srCNAM.data_size + 6
		
		self.srSNAM = self.SNAM()
		self.srSNAM = self.read_record(self.srSNAM, f)

		self.srMAST_DATA = []
		while True: 
			srMAST = self.MAST()
			srMAST = self.read_record(srMAST, f)
			if srMAST: 
				srDATA = self.DATA()
				srDATA = self.read_record(srDATA, f)
				self.srMAST_DATA.append((srMAST, srDATA))
				read_size += srMAST.data_size + 6
				read_size += srDATA.data_size + 6
			else: 
				break

		self.srINTV = self.INTV()
		self.srINTV = self.read_record(self.srINTV, f)
		read_size += self.srINTV.data_size + 6

		self.srINCC = self.INCC()
		self.srINCC = self.read_record(self.srINCC, f)
		print(read_size)
		return self

	def write(self, f): 
		f.write(self.type.encode("utf-8"))
		f.write(struct.pack("4I", self.data_size, self.flags, self.id, self.rev))
#		f.write(self.data_size.to_bytes(4, byteorder="little"))
#		f.write(self.flags.to_bytes(4, byteorder="little"))
#		f.write(self.id.to_bytes(4, byteorder="little"))
#		f.write(self.rev.to_bytes(4, byteorder="little"))
		f.write(struct.pack("HH", self.version, self.unknown))
#		f.write(self.version.to_bytes(2, byteorder="little"))
#		f.write(self.unknown.to_bytes(2, byteorder="little"))

#		self.srHEDR = self.HEDR()
#		self.srHEDR = self.read_record(self.srHEDR, f)
#		read_size += self.srHEDR.data_size + 6
#		
#		self.srCNAM = self.CNAM()
#		self.srCNAM = self.read_record(self.srCNAM, f)
#		read_size += self.srCNAM.data_size + 6
#		
#		self.srSNAM = self.SNAM()
#		self.srSNAM = self.read_record(self.srSNAM, f)
#
#		self.srMAST_DATA = []
#		while True: 
#			srMAST = self.MAST()
#			srMAST = self.read_record(srMAST, f)
#			if srMAST: 
#				srDATA = self.DATA()
#				srDATA = self.read_record(srDATA, f)
#				self.srMAST_DATA.append((srMAST, srDATA))
#				read_size += srMAST.data_size + 6
#				read_size += srDATA.data_size + 6
#			else: 
#				break
#
#		self.srINTV = self.INTV()
#		self.srINTV = self.read_record(self.srINTV, f)
#		read_size += self.srINTV.data_size + 6
#
#		self.srINCC = self.INCC()
#		self.srINCC = self.read_record(self.srINCC, f)
#		print(read_size)
#		return self
	
	def get_sr_def(self): 
		sr_def = []
		sr_def.append(("+", "HEDR", "struct", "Contains additional details about the plugin, see section below"))
		sr_def.append(("-", "CNAM", "struct", "author"))
		sr_def.append(("-", "SNAM", "struct", "description"))
		sr_def.append(("*", ["MAST", "DATA"], ["struct", "struct"], "Data on the plugin's master files, listed in the order they were present in when the plugin was written."))
		return sr_def
	
	class HEDR(Record): 
		def __init__(self):
			self.type = "HEDR"
			self.optional = False
			self.data_size = -1
			self.version = None
			self.numRecords = None
			self.nextObjectId = None
		
		def read(self, f): 
			self.check_type(f)
			self.data_size = readU16(f)
			self.version = readFloat(f)
			self.numRecords = read32(f)
			self.nextObjectId = readULong(f)
			return self
		
		def get_sr_def(self): 
			sr_def = []
			#sr_def.append(("+", "version"	float	0.94 in most files; 1.7 in recent versions of Update.esm.

	class CNAM(StringRecord): 
		def __init__(self):
			StringRecord.__init__(self, "CNAM", True)
			
	class SNAM(StringRecord): 
		def __init__(self):
			StringRecord.__init__(self, "SNAM", True)

	class MAST(StringRecord): 
		def __init__(self):
			StringRecord.__init__(self, "MAST", True)
	
	class DATA(Record): 
		def __init__(self):
			self.type = "DATA"
			self.optional = True
			self.data_size = -1
			self.fileSize = -1
		
		def read(self, f): 
			self.check_type(f)
			self.data_size = readU16(f)
			self.fileSize = readU64(f)
			return self

	class INTV(Record): 
		def __init__(self):
			self.type = "INTV"
			self.optional = False
			self.data_size = -1
			self.unknown = None
		
		def read(self, f): 
			self.check_type(f)
			self.data_size = readU16(f)
			self.unknown = readU32(f)
			return self

	class INCC(Record): 
		def __init__(self):
			self.type = "INCC"
			self.optional = True
			self.unknown = None
		
		def read(self, f): 
			self.check_type(f)
			self.unknown = readU32(f)
			return self