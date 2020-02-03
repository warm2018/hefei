
with open('phase.xml', 'w') as routes1:
	with open ("phase2.xml","r") as routes2:
		for line in routes2:
			line0 = line.replace('\n','')
			new_line = line0.replace('rrrG','rrGG')
			new1_line = new_line.replace('GGGr','GGrr')
			print(new1_line,file=routes1)





