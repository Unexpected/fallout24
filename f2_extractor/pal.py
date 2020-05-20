"""
Copyright 2014-2015 darkf

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# Fallout 2 .PAL palette parser

import sys, os, struct

def readPAL(f):
	palette = [None]*256

	for i in range(256):
		r,g,b = ord(f.read(1)), ord(f.read(1)), ord(f.read(1))

		if r <= 63 and g <= 63 and b <= 63: # valid palette colors are 0..63
			r *= 4
			g *= 4
			b *= 4
		else:
			r = 0
			g = 0
			b = 0

		palette[i] = (r, g, b)

	return palette

def readColorTable(f):
	f.seek(256*3)
	return map(ord, f.read(0x8000))

def main():
	if len(sys.argv) != 2:
		print("USAGE: %s PAL" % sys.argv[0])
		sys.exit(1)

	with open(sys.argv[1], "rb") as f:
		print(readPAL(f))

if __name__ == '__main__':
	main()