
file_new = file
file_old = file+"ini"
shutil.copy(file_new, file_old)

f = open(file_old,"r")
DATA = []
for line in f:
	row = line.split("\t")
	DATA.append([float(row[0]) , float(row[1])])

f.close()


f = open(file_new,"w")
for row in DATA:
	f.write(str(int(row[0])) + "\t" + str(int(row[1])) + "\n")
f.close()

