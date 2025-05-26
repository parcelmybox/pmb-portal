#!/usr/bin/env python3
import sys 

example=f'''python3 {sys.argv[0]} prashanth dublin'''

if len(sys.argv) < 3:
	print("Please run python3 "+ sys.argv[0]+ " <name> <city> ")
	print(example)
	sys.exit(1)

name=sys.argv[1]
city=sys.argv[2]

address=f'''
Ravi @{name} {city}  Flat no 2409, block 2 
Panchavati apartments , 
Pragathi Nagar; Hyderabad 500090 , Phonoe: +91 92474 99247'''


print(address)
