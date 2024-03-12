# Student Authors: Álvaro Terroso, Pedro Lima, Tiago Marques
# Author: Marco Simoes
# Adapted from Java's implementation of Rui Pedro Paiva
# Teoria da Informacao, LEI, 2022

import sys
from huffmantree import HuffmanTree


class GZIPHeader:
	''' class for reading and storing GZIP header fields '''

	ID1 = ID2 = CM = FLG = XFL = OS = 0
	MTIME = []
	lenMTIME = 4
	mTime = 0

	# bits 0, 1, 2, 3 and 4, respectively (remaining 3 bits: reserved)
	FLG_FTEXT = FLG_FHCRC = FLG_FEXTRA = FLG_FNAME = FLG_FCOMMENT = 0   
	
	# FLG_FTEXT --> ignored (usually 0)
	# if FLG_FEXTRA == 1
	XLEN, extraField = [], []
	lenXLEN = 2
	
	# if FLG_FNAME == 1
	fName = ''  # ends when a byte with value 0 is read
	
	# if FLG_FCOMMENT == 1
	fComment = ''   # ends when a byte with value 0 is read
		
	# if FLG_HCRC == 1
	HCRC = []
		
		
	
	def read(self, f):
		''' reads and processes the Huffman header from file. Returns 0 if no error, -1 otherwise '''

		# ID 1 and 2: fixed values
		self.ID1 = f.read(1)[0]  
		if self.ID1 != 0x1f: return -1 # error in the header
			
		self.ID2 = f.read(1)[0]
		if self.ID2 != 0x8b: return -1 # error in the header
		
		# CM - Compression Method: must be the value 8 for deflate 
		self.CM = f.read(1)[0]
		if self.CM != 0x08: return -1 # error in the header
					
		# Flags
		self.FLG = f.read(1)[0]
		
		# MTIME
		self.MTIME = [0]*self.lenMTIME
		self.mTime = 0
		for i in range(self.lenMTIME):
			self.MTIME[i] = f.read(1)[0]
			self.mTime += self.MTIME[i] << (8 * i) 				
						
		# XFL (not processed...)
		self.XFL = f.read(1)[0]
		
		# OS (not processed...)
		self.OS = f.read(1)[0]
		
		# --- Check Flags
		self.FLG_FTEXT = self.FLG & 0x01
		self.FLG_FHCRC = (self.FLG & 0x02) >> 1
		self.FLG_FEXTRA = (self.FLG & 0x04) >> 2
		self.FLG_FNAME = (self.FLG & 0x08) >> 3
		self.FLG_FCOMMENT = (self.FLG & 0x10) >> 4
					
		# FLG_EXTRA
		if self.FLG_FEXTRA == 1:
			# read 2 bytes XLEN + XLEN bytes de extra field
			# 1st byte: LSB, 2nd: MSB
			self.XLEN = [0]*self.lenXLEN
			self.XLEN[0] = f.read(1)[0]
			self.XLEN[1] = f.read(1)[0]
			self.xlen = self.XLEN[1] << 8 + self.XLEN[0]
			
			# read extraField and ignore its values
			self.extraField = f.read(self.xlen)
		
		def read_str_until_0(f):
			s = ''
			while True:
				c = f.read(1)[0]
				if c == 0: 
					return s
				s += chr(c)
		
		# FLG_FNAME
		if self.FLG_FNAME == 1:
			self.fName = read_str_until_0(f)
		
		# FLG_FCOMMENT
		if self.FLG_FCOMMENT == 1:
			self.fComment = read_str_until_0(f)
		
		# FLG_FHCRC (not processed...)
		if self.FLG_FHCRC == 1:
			self.HCRC = f.read(2)
			
		return 0
			



class GZIP:
	''' class for GZIP decompressing file (if compressed with deflate) '''

	gzh = None
	gzFile = ''
	fileSize = origFileSize = -1
	numBlocks = 0
	f = None
	

	bits_buffer = 0
	available_bits = 0		

	
	def __init__(self, filename):
		self.gzFile = filename
		self.f = open(filename, 'rb')
		self.f.seek(0,2)
		self.fileSize = self.f.tell()
		self.f.seek(0)

		
	

	def decompress(self):
		''' main function for decompressing the gzip file with deflate algorithm '''
		
		numBlocks = 0

		# get original file size: size of file before compression
		origFileSize = self.getOrigFileSize()
		print(origFileSize)
		
		# read GZIP header
		error = self.getHeader()
		if error != 0:
			print('Formato invalido!')
			return
		
		# show filename read from GZIP header
		print(self.gzh.fName)
		
		
		# MAIN LOOP - decode block by block
		BFINAL = 0	
		while not BFINAL == 1:	
			
			BFINAL = self.readBits(1)
							
			BTYPE = self.readBits(2)					
			if BTYPE != 2:
				print('Error: Block %d not coded with Huffman Dynamic coding' % (numBlocks+1))
				return
			
									
			#--- STUDENTS --- ADD CODE HERE
			# 
			# 
			#helping variables
			verbose = True
			SIZE = 20
			MAXLEN = 8		
			print("\nExercício 1\n")

			#read block header
			HLIT = self.readBits(5)
			HDIST = self.readBits(5)
			HCLEN = self.readBits(4)

			HLIT += 257
			HDIST += 1
			HCLEN += 4

			print("HLIT:" + str(HLIT))
			print("HDIST:" + str(HDIST))
			print("HCLEN: " + str(HCLEN))

			arr_order = [16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15]
			HCLEN_arr = [0 for i in range(SIZE)]

			print("\nExercício 2\n")

			#read lens in 3bit chunks
			for i in range(HCLEN):
				HCLEN_arr[arr_order[i]] = self.readBits(3)		
			print(HCLEN_arr)

			print("\nExercício 3\n")
			#initialize count lens
			bl_count = [0 for i in range(MAXLEN)]
			
			#count lens
			for comp in HCLEN_arr:
				bl_count[comp]+= 1	
			
			#first huffman code for each len
			bl_count[0] = 0
			next_code = [0 for i in range(MAXLEN)]
			code = 0
			for i in range(1,MAXLEN):
				code = (code + bl_count[i-1]) << 1
				next_code[i] = code

			#generate final huffman codes
			final_code = [0 for i in range(SIZE)]
			for i in range(SIZE):
				comp = HCLEN_arr[i]
				if comp != 0:
					final_code[i] = next_code[comp]
					next_code[comp] += 1
			print(final_code)
		
			#de modo a ficar certo na árvore fazemos rjust, ex: quando temps 0 fica 000
			bin_code = [(bin(final_code[i]))[2:].rjust(HCLEN_arr[i], '0') for i in range(SIZE)]
			
			for i in range(SIZE):
				if HCLEN_arr[i]==0:
					bin_code[i] = ''
			print(bin_code)

			#turn huffman codes from array to tree
			hftlen = HuffmanTree()	
			for i in range(len(bin_code)):
				if(bin_code[i] != ''):
					hftlen.addNode(bin_code[i],i,verbose) #put true to debug huffman tree
		
			# --------- EXERCÍCIO 4 ----------
			
			print("\nExercício 4\n")
			hlit_arr = self.arrayFromTree(hftlen, HLIT)
			print(hlit_arr)

			# --------- EXERCÍCIO 5 ----------

			print("\nExercício 5\n")
			hdist_arr = self.arrayFromTree(hftlen, HDIST)
			print(hdist_arr)

			# --------- EXERCÍCIO 6 ----------

			print("\nExercício 6 (HLIT)\n")
			bincodelit,finalcodelit = self.createHuffmanCode(hlit_arr,HLIT,SIZE)
			print(bincodelit)
			if verbose: print(finalcodelit)
			if verbose: print("\nGenerating tree...")
			hftlit = HuffmanTree()
			for i in range(len(bincodelit)):
				if(bincodelit[i] != ''):
					hftlit.addNode(bincodelit[i],i,verbose) #put true to debug huffman tree

			print("\nExercício 6 (HDIST)\n")
			bincodedist = []
			finalcodedist = []
			bincodedist,finalcodedist = self.createHuffmanCode(hdist_arr,HDIST,SIZE)
			print(bincodedist)
			if verbose: print(finalcodedist)
			if verbose: print("\nGenerating tree...")
			hftdist = HuffmanTree()	
			for i in range(len(bincodedist)):
				if(bincodedist[i] != ''):
					hftdist.addNode(bincodedist[i],i,verbose) #put true to debug huffman tree

			# --------- EXERCÍCIO 7 ----------

			print("\nExercício 7\n")

			code = 0
			if numBlocks == 0: 
				count = 0
				finalarr = []

			if count-32768>=0:
				finalarr = finalarr[count-32768:]
				count = len(finalarr)


			startindex = len(finalarr)

			while(code != 256):
				code = self.readTreeBitByBit(hftlit)
				if code == 256: continue
				elif code<256:
					finalarr.append(code)
					count+= 1
				else:
					#gets C value
					if code>284: c = 258
					else:
						c = code-254
						if code>264:
							for i in range(265,code):
								bit = (i-261)//4 #265,266,269 -> 4//4=1 5//4=1, 8//4 =2... 
								c += ((2**bit)-1)
							bit = (code-261)//4
							c += self.readBits(bit)	
					#gets D value
					code2 = self.readTreeBitByBit(hftdist)
					d = code2+1
					if code2>3:
						for i in range(4,code2):
							bit = (i-2)//2
							d+= ((2**bit)-1)
						bit = (code2-2)//2
						if(bit>0): d += self.readBits(bit)
					#does LZ77(C,D)
					startsize = len(finalarr)
					for i in range(c):
						if d<startsize:
							#finalarr aumenta cada vez que é iterado, então -d é estático
							finalarr.append(finalarr[-d])
							count += 1
			

			# --------- EXERCÍCIO 8 ----------

			print("\nExercício 8\n")
			if numBlocks == 0: print("<To see additional information, set verbose to True>\n")
		
			with open(GZIPHeader.fName, 'ab') as Ficheiro:
				Ficheiro.write(bytes(finalarr[startindex:]))

			print("Saving block to "+GZIPHeader.fName)
			# --------- END ----------
			numBlocks += 1 # update number of blocks read	
		self.f.close() # close file
		print("End: %d block(s) analyzed." % numBlocks)
	
	#Function created to streamline huffman code creation for hlit and hdist
	def createHuffmanCode(self, lenarr, size, maxlen):
		bl_count = [0 for i in range(maxlen)]
		#count lens
		for comp in lenarr:
			bl_count[comp]+= 1	
		#first huffman code for each len
		bl_count[0] = 0
		next_code = [0 for i in range(maxlen)]
		code = 0
		for i in range(1,maxlen):
			code = (code + bl_count[i-1]) << 1
			next_code[i] = code 
		#generate final huffman codes
		final_code = [0 for i in range(size)]
		for i in range(size):
			comp = lenarr[i]
			if comp != 0:
				final_code[i] = next_code[comp]
				next_code[comp] += 1
		#generate huffman codes in binary string format
		bin_code = [(bin(final_code[i]))[2:].rjust(lenarr[i], '0') for i in range(size)]
		for i in range(size):
			if lenarr[i]==0:
				bin_code[i] = ''
		return bin_code,final_code

	#Function created to streamline creation of arrays to be huffed
	def arrayFromTree(self, hft, size):
		hft.resetCurNode()
		arr = [0 for i in range(size)]
		i = 0
		while i < size:
			node = self.readTreeBitByBit(hft)
			if node == 16:
				for j in range(3+self.readBits(2)):
					arr[i] = arr[i-1]
					i+=1
			elif node == 17:
				for j in range(3+self.readBits(3)):
					arr[i] = 0
					i+=1
			elif node == 18:
				repeat = 11+self.readBits(7)
				for j in range(repeat):
					arr[i] = 0
					i+=1
			else:
				arr[i] = node
				i+=1
		return arr

	#Function created to streamline reading a tree bit by bit until a leaf is found
	def readTreeBitByBit(self,hft):
		hft.resetCurNode()
		while True:
			nextBit = self.readBits(1)
			node = hft.nextNode(str(nextBit))
			#this is here for optimization
			if node == -2: continue
			elif node == -1:
				print("Something is wrong with the tree")
				exit()
			else:
				return node

	def getOrigFileSize(self):
		''' reads file size of original file (before compression) - ISIZE '''
		
		# saves current position of file pointer
		fp = self.f.tell()
		
		# jumps to end-4 position
		self.f.seek(self.fileSize-4)
		
		# reads the last 4 bytes (LITTLE ENDIAN)
		sz = 0
		for i in range(4): 
			sz += self.f.read(1)[0] << (8*i)
		
		# restores file pointer to its original position
		self.f.seek(fp)
		
		return sz		
	

	
	def getHeader(self):  
		''' reads GZIP header'''

		self.gzh = GZIPHeader()
		header_error = self.gzh.read(self.f)
		return header_error
		

	def readBits(self, n, keep=False):
		''' reads n bits from bits_buffer. if keep = True, leaves bits in the buffer for future accesses '''

		while n > self.available_bits:
			self.bits_buffer = self.f.read(1)[0] << self.available_bits | self.bits_buffer
			self.available_bits += 8
		
		mask = (2**n)-1
		value = self.bits_buffer & mask

		if not keep:
			self.bits_buffer >>= n
			self.available_bits -= n

		return value



if __name__ == '__main__':

	# gets filename from command line if provided
	fileName = "Samples/sample_audio.mp3.gz"
	if len(sys.argv) > 1:
		fileName = sys.argv[1]			

	# decompress file
	GZIPHeader.fName = "Samples/sample_audio_3.mp3"
	gz = GZIP(fileName)
	gz.decompress()
