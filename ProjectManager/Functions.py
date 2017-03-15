#! /usr/bin/python

#Definition of the function which extract the coordinates of the root path associating the root, plant and genotype informations. It returns a list named Data and has as an argument the type of plant or genotype you want to study.

def extract_germination (Type):
	import os, sys, fnmatch
	Array = []
	memory_genotype = ""
	memory_filename = ""

	#The following loop searches in the folders (sorted by alphabetical order) of the database all the file names which end by "*_OUT_.txt" and begins by Type (the argument of the function).

	for dirpath, dirs, files in os.walk('E:\\CIRC_DATABASE\\'):
		dirs.sort()
		files.sort()
		#For each file names, we join the file name to its folder path to obtain the file path from which we extract the plant caracteristics (genotype + replicate) with the split method.

		for filename in fnmatch.filter(files, Type + "*_OUT_.txt"):
			file_path = os.path.join(dirpath, filename)

			split = file_path.split ('\\')
			n = len (split)
			#the last element of the list gives the file name
			file_name = split [n-1]
			split2 = file_name.split ('_')
			#the genotype is the third element of the list after the name of the species and the categorie within it (like Spring or Winter for Barley)
			genotype = split2[2]

			if memory_genotype == "" :
				memory_genotype = genotype
				memory_filename = file_name

			fl = open(file_path)
			counter_plant = 0
			counter_globals = 0
			plant = False

			#We read all the files one by one line by line. For each line, we check the presence of fixed characters to extract the information needed. We count the number of plants and roots for each file.

			for line in fl :

				#If no seeds germed, there is no use to make additional checks so we use a break.

				if "NO GERMINATION" in line :
					if genotype == memory_genotype and filename != memory_filename:
						Array.append ([genotype, 0])
						memory_genotype = ""
					break			
				
				#If there is a plant registered, we count it and initialise some variables for the root information extraction like the counter and a boolean which is true if there is at least one root for a plant registered.

				if "Plant:" in line:
					plant = True
					continue

				if ("Root:" in line) and plant == True:
					if counter_plant != 3 :
						counter_plant = counter_plant + 1
						plant = False
					continue
				
					#We need now to add the coordinates to Data. We do it when we encounter a new root or when the plant data ends (with "Globals")
			
			fl.close()
			if genotype == memory_genotype and filename != memory_filename:
				Array.append ([genotype, counter_plant])
				memory_genotype = ""
			elif genotype != memory_genotype:
				memory_genotype = genotype
	return Array

#Definition of the function which extract the coordinates of the root path associating the root, plant and genotype informations. It returns a list named Data and has as an argument the type of plant or genotype you want to study.

def extract_data (path):
	import os, sys, fnmatch
	Data = []
	cur_data = []
	pop = ""
	#The following loop searches in the folders (sorted by alphabetical order) of the database all the file names which end by "*_OUT_.txt" and begins by Type (the argument of the function).

	for dirpath, dirs, files in os.walk(path + "\\"):
		dirs.sort()
		files.sort()
		#For each file names, we join the file name to its folder path to obtain the file path from which we extract the plant caracteristics (genotype + replicate) with the split method.

		for filename in fnmatch.filter(files,"*_OUT_.txt"):
			file_path = os.path.join(dirpath, filename)
			#print(file_path)

			split = file_path.split ('\\')
			n = len (split)
			#the last element of the list gives the file name
			file_name = split [n-1]
			split2 = file_name.split ('_')
			#the genotype is the third element of the list after the name of the species and the categorie within it (like Spring or Winter for Barley)
			genotype = split2[2]
			var = split2[0] + "_" + split2[1]
			if (var) != pop:
				if cur_data != []:
					Data.append([pop,cur_data])
				pop = var
				cur_data = []

			fl = open(file_path)
			counter_plant = 0

			#We read all the files one by one line by line. For each line, we check the presence of fixed characters to extract the information needed. We count the number of plants and roots for each file.

			for line in fl :

				#If no seeds germed, there is no use to make additional checks so we use a break.

				if "NO GERMINATION" in line :
					break			
				
				#If there is a plant registered, we count it and initialise some variables for the root information extraction like the counter and a boolean which is true if there is at least one root for a plant registered.

				if "Plant:" in line:
					counter_plant = counter_plant + 1
					counter_root = 0
					root = False
					continue
				
				#If we find a root, we count it and we make root true.

				
				if "Root:" in line :
					counter_root = counter_root + 1
					root = True
			
				#If we found at least one root, we check for the coordinates, one line with X and one with Y and then add these coordinates to Data.

			
				if root == True :

					#To extract the coordinates, we delete some non coordinates elements (the lay-out elements and the "X:") the line then read all the elements of the list created by splitting using the "," character. We reinitialise X each new X line encountered.

					if "X" in line:
						X = []
						line = line.replace('\t','')
						line = line.replace("X","")
						line = line.replace(":","")
						line = line.replace("\r","")
						line = line.replace("\n","")	
					
						rowx = line.split(',')
	
						if rowx[0] == "":
							del rowx[0]

						nx = len(rowx)
					 	
						#With this loop, we add the numbers corresponding to the coordinates to a list named X with the append function converting the strings obtained.
			
						for i in range(0,nx-1):
							X.append(float(rowx[i]))
						
						continue
		
					if "Y" in line:
						Y = []
						line = line.replace('\t','')
						line = line.replace("Y","")
						line = line.replace(":","")
						line = line.replace("\r","")
						line = line.replace("\n","")	
				
						rowy = line.split(',')
				
						if rowy[0] == "":
							del rowy[0]

						ny = len(rowy)
				
						for i in range(0,ny-1):
							Y.append(float(rowy[i]))

						continue
		
					#We need now to add the coordinates to Data. We do it when we encounter a new root or when the plant data ends (with "Globals").

					if "Globals" in line:	
						cur_data.append([genotype,counter_plant-1,counter_root,X,Y,file_name])
						continue
					
					if  counter_root > 1 :
						cur_data.append([genotype,counter_plant-1,counter_root-1,X,Y,file_name])
			
			fl.close()
	Data.append([pop,cur_data])
	return Data



#Definition of the function which calculates the mean length of the root of any population (from the replicate to the entire species) using Data from extract_data.

def get_length (root):

	import os, sys, math

	#We initialise length.
		
	#The X coordinates are contained in the list which is the fourth column of the list root.
	rootx = root[3]
	#The Y coordinates are contained in the list which is the fifth column of the list root.
	rooty = root[4]
	length = 0.0
	number = len (rootx)

	#The following loop reads each x and y coordinates from Data one by one registering the previous ones to calculate the length between two following points. Then it adds all the lengths for one root and registers the sum in a list named data_length.

	for i in range (0, number):
		#registration of the previous values.
		if i != 0:
			xp = xa
			yp = ya

		xa = rootx[i]
		ya = rooty[i]

		#Addition of the lengths using the Pythagore method.
		if i != 0:
			length = length + math.sqrt((xa-xp)*(xa-xp) + (yp - ya)*(yp - ya))

	return length


def get_x(data, i) :
	import os, sys
	root = data[i]
	x = root[3]
	return x

def get_y(data, i) :
	import os, sys
	root = data[i]
	y = root[4]
	return y

def get_length_data (Data,age,Result):
	n = len(Data)
	#This loop reads all Data element by element and create the list of lengths with get_length.
	data_length = []
	genotype = ""
	file_name = ""

	for j in range (0, n):
		root = Data[j]

		if genotype == "":
			if age == "old":
				plant = -1
				total = 0
				maxi = 0
				if Result == "P":
					maxi_total = 0
				counter_root = 0
				counter_plant = 0
			elif age == "young":
				length = get_length(root)
				counter_root = 0
				total = 0
				if Result == "P":
					maxi_total = 0
				maxi = length
				counter_plant = 1		
				plant = root[1]
			genotype = root[0]
			file_name = root[5]
			mean = 0.0
			if Result == "P":
				maxi_mean = 0

		if age == "old":
			if root [5] != file_name:
				check = True
			else:
				check = False
		elif age == "young":
			if root [5] == file_name:
				check = True
			else:
				check = False

		if root[0] == genotype and check == True:

			if root[1] != plant:
				if maxi != 0:
					if Result == "P":
						maxi_total = maxi_total + maxi
					elif Result == "S":
						mean = total/counter_root
						data_length.append([genotype,counter_plant,plant,counter_root,total,mean,maxi])
						total = 0
						counter_root = 0
					maxi = 0
				counter_plant = counter_plant + 1
				plant = root[1]

			length = get_length (root)
			total = total + length
			counter_root = counter_root + 1

			if length > maxi:
				maxi = length

		elif root[0] != genotype and counter_root != 0 and counter_plant != 0:
			if Result == "P":
				maxi_total = maxi_total + maxi
				total_mean = total/counter_plant
				maxi_mean = maxi_total/counter_plant
				root_number = float(counter_root)/float(counter_plant)
				mean = total/counter_root
				data_length.append ([genotype,root_number,total_mean,mean,maxi_mean,counter_plant,counter_root,total,maxi_total])
			elif Result == "S":
				mean = total/counter_root
				data_length.append([genotype,counter_plant,plant,counter_root,total,mean,maxi])
			if age == "old":
				counter_plant = 0
				counter_root = 0
				total = 0
				maxi = 0
				if Result == "P":
					maxi_total = 0
				plant = -1
			elif age == "young":
				counter_plant = 1
				counter_root = 1
				length = get_length(root)
				total = length
				maxi = length
				if Result == "P":
					maxi_total = 0
				plant = root[1]
			if Result == "P":
				maxi_mean = 0
			mean = 0.0
			genotype = root[0]
			file_name = root[5]
		
		elif root [0] != genotype and counter_root == 0:
			genotype = ""

	if Result == "P" and counter_plant != 0:
		maxi_total = maxi_total + maxi
		total_mean = total/counter_plant
		maxi_mean = maxi_total/counter_plant
		root_number = float(counter_root)/float(counter_plant)
		mean = total/counter_root
		data_length.append ([genotype,root_number,total_mean,mean,maxi_mean,counter_plant,counter_root,total,maxi_total])
	elif Result == "S" and counter_root != 0:
		mean = total/counter_root
		data_length.append([genotype,counter_plant,plant,counter_root,total,mean,maxi])
	return data_length

def get_angle_data (Data,age,Result):
	import os,sys,math
	n = len(Data)
	#This loop reads all Data element by element and create the list of lengths with get_length.
	data_angle = []
	genotype = ""
	file_name = ""

	for j in range (0, n):
		root = Data[j]

		if genotype == "":
			if age == "old":
				plant = -1

				total_start_angle = 0
				maxi_start_angle = -(math.pi + 1)
				top_start_angle = math.pi + 1
				second_top_start_angle = -(2*math.pi + 1)
				mini_start_angle = math.pi + 1
				
				total_tip_angle = 0
				maxi_tip_angle = -(math.pi + 1)
				top_tip_angle = math.pi + 1
				second_top_tip_angle = -(2*math.pi + 1)
				mini_tip_angle = math.pi + 1

				counter_root = 0
				counter_root_plant = 0
				counter_plant = 0
			elif age == "young":
				x_root = get_x(Data,j)
				y_root = get_y(Data,j)
				length_x_root = len(x_root)
				x_init = x_root[0]
				y_init = y_root[0]
				start_angle_x = 0.0
				start_angle_y = 0.0
				start_angle = 0.0

				end = int(length_x_root/4)
				for i in range(1, end + 1):
					start_angle_x = start_angle_x + (x_root[i] - x_init)
					start_angle_y = start_angle_y + (y_init - y_root[i])
					start_angle = start_angle + math.atan2(start_angle_y,start_angle_x)
				start_angle = start_angle/end
	
				tip_angle_x = x_root[length_x_root-1] - x_init
				tip_angle_y = y_init - y_root[length_x_root-1]
				tip_angle = math.atan2(tip_angle_y,tip_angle_x)

				total_start_angle = 0
				maxi_start_angle = start_angle
				if start_angle - math.pi/2 >= 0:
					top_start_angle = start_angle - math.pi/2
					second_top_start_angle = -(math.pi + 1)
				else:
					top_start_angle = math.pi + 1
					second_top_start_angle = start_angle - math.pi/2
				mini_start_angle = start_angle
				
				total_tip_angle = 0
				maxi_tip_angle = tip_angle
				if tip_angle - math.pi/2 >= 0:
					top_tip_angle = tip_angle - math.pi/2
					second_top_tip_angle = -(2*math.pi + 1)
				else:
					top_tip_angle = math.pi + 1
					second_top_tip_angle = tip_angle - math.pi/2
				mini_tip_angle = tip_angle

				plant = root[1]
				counter_plant = 1
				counter_root_plant = 0
				counter_root = 0

			genotype = root[0]
			file_name = root[5]

		if age == "old":
			if root [5] != file_name:
				check = True
			else:
				check = False
		elif age == "young":
			if root [5] == file_name:
				check = True
			else:
				check = False

		if root[0] == genotype and check == True:

			if root[1] != plant:
				if plant != -1:
					if counter_root_plant != 1:
						if maxi_start_angle != -(math.pi + 1) and mini_start_angle != math.pi + 1 and maxi_start_angle != mini_start_angle:
							if top_start_angle != math.pi + 1 and second_top_start_angle != -(2*math.pi + 1):
								total_start_angle = total_start_angle + 2 * math.pi - (top_start_angle - second_top_start_angle)
							elif top_start_angle == math.pi + 1 or top_start_angle < 0:
								total_start_angle = total_start_angle + (maxi_start_angle - mini_start_angle)
						if maxi_tip_angle != -(math.pi + 1) and mini_tip_angle != math.pi + 1 and maxi_tip_angle != mini_tip_angle:
							if top_tip_angle != math.pi + 1 and second_top_tip_angle != -(2*math.pi + 1):
								total_tip_angle = total_tip_angle + 2 * math.pi - (top_tip_angle - second_top_tip_angle)
							elif top_tip_angle == math.pi + 1 or top_tip_angle < 0:
								total_tip_angle = total_tip_angle + (maxi_tip_angle - mini_tip_angle)
					else:
						total_start_angle = total_start_angle + abs(start_angle)
						total_tip_angle = total_tip_angle + abs(tip_angle)

					if Result == "S":
						if counter_root_plant != 0:
							total_start_angle = math.degrees(total_start_angle)
							total_tip_angle = math.degrees(total_tip_angle)
							data_angle.append ([genotype,counter_plant,plant,counter_root_plant,total_start_angle,total_tip_angle])
						total_start_angle = 0
						total_tip_angle = 0

				counter_plant = counter_plant + 1
				counter_root_plant = 1
				plant = root[1]
				

				maxi_start_angle = -(math.pi + 1)
				top_start_angle = math.pi + 1
				second_top_start_angle = -(2*math.pi + 1)
				mini_start_angle = math.pi + 1

				maxi_tip_angle = - (math.pi + 1)
				top_tip_angle = math.pi + 1
				second_top_tip_angle = -(2*math.pi + 1)
				mini_tip_angle = math.pi + 1

			else:
				counter_root_plant = counter_root_plant + 1

			counter_root = counter_root + 1

			x_root = get_x(Data,j)
			y_root = get_y(Data,j)
			length_x_root = len(x_root)
			x_init = x_root[0]
			y_init = y_root[0]
			start_angle_x = 0.0
			start_angle_y = 0.0
			start_angle = 0.0

			end = int(length_x_root/4)
			for i in range(1, end + 1):
				start_angle_x = start_angle_x + (x_root[i] - x_init)
				start_angle_y = start_angle_y + (y_init - y_root[i])
				start_angle = start_angle + math.atan2(start_angle_y,start_angle_x)
			start_angle = start_angle/end

			tip_angle_x = x_root[length_x_root-1] - x_init
			tip_angle_y = y_init - y_root[length_x_root-1]
			tip_angle = math.atan2(tip_angle_y,tip_angle_x)

			if start_angle > maxi_start_angle:
				maxi_start_angle = start_angle
			if start_angle - math.pi/2 >= 0 and start_angle - math.pi/2 < top_start_angle:
				top_start_angle = start_angle - math.pi/2
			if start_angle - math.pi/2 < 0 and start_angle - math.pi/2 > second_top_start_angle:
				second_top_start_angle = start_angle - math.pi/2
			if start_angle < mini_start_angle:
				mini_start_angle = start_angle
			if tip_angle > maxi_tip_angle:
				maxi_tip_angle = tip_angle
			if tip_angle - math.pi/2 >= 0 and tip_angle - math.pi/2 < top_tip_angle:
				top_tip_angle = tip_angle - math.pi/2
			if tip_angle - math.pi/2 < 0 and tip_angle - math.pi/2 > second_top_tip_angle:
				second_top_tip_angle = tip_angle - math.pi/2
			if tip_angle < mini_tip_angle:
				mini_tip_angle = tip_angle
			
		elif root[0] != genotype and counter_root != 0 and counter_plant != 0:
			if counter_root_plant != 1:
				if maxi_start_angle != -(math.pi + 1) and mini_start_angle != math.pi + 1 and maxi_start_angle != mini_start_angle:
					if top_start_angle != math.pi + 1 and second_top_start_angle != -(2*math.pi + 1):
						total_start_angle = total_start_angle + 2 * math.pi - (top_start_angle - second_top_start_angle)
					elif top_start_angle == math.pi + 1 or top_start_angle < 0:
						total_start_angle = total_start_angle + (maxi_start_angle - mini_start_angle)
				if maxi_tip_angle != -(math.pi + 1) and mini_tip_angle != math.pi + 1 and maxi_tip_angle != mini_tip_angle:
					if top_tip_angle != math.pi + 1 and second_top_tip_angle != -(2*math.pi + 1):
						total_tip_angle = total_tip_angle + 2 * math.pi - (top_tip_angle - second_top_tip_angle)
					elif top_tip_angle == math.pi + 1 or top_tip_angle < 0:
						total_tip_angle = total_tip_angle + (maxi_tip_angle - mini_tip_angle)
			else:
				total_start_angle = total_start_angle + abs(start_angle)
				total_tip_angle = total_tip_angle + abs(tip_angle)


			if Result == "P":
				total_start_angle = math.degrees(total_start_angle / counter_plant)
				total_tip_angle = math.degrees(total_tip_angle / counter_plant)

				root_number = float(counter_root)/float(counter_plant)
			
				data_angle.append ([genotype,root_number,total_start_angle,total_tip_angle,counter_plant])

			elif Result == "S" and counter_root_plant !=0:
				total_start_angle = math.degrees(total_start_angle)
				total_tip_angle = math.degrees(total_tip_angle)
				data_angle.append ([genotype,counter_plant,plant,counter_root_plant,total_start_angle,total_tip_angle])

			if age == "old":
				plant = -1

				total_start_angle = 0
				maxi_start_angle = -(math.pi + 1)
				top_start_angle = math.pi + 1
				second_top_start_angle = -(2*math.pi + 1)
				mini_start_angle = math.pi + 1
				
				total_tip_angle = 0
				maxi_tip_angle = -(math.pi + 1)
				top_tip_angle = math.pi + 1
				second_top_tip_angle = -(2*math.pi + 1)
				mini_tip_angle = math.pi + 1

				counter_root = 0
				counter_root_plant = 0
				counter_plant = 0
			elif age == "young":
				x_root = get_x(Data,j)
				y_root = get_y(Data,j)
				length_x_root = len(x_root)
				x_init = x_root[0]
				y_init = y_root[0]
				start_angle_x = 0.0
				start_angle_y = 0.0
				start_angle = 0.0

				end = int(length_x_root/4)
				for i in range(1, end + 1):
					start_angle_x = start_angle_x + (x_root[i] - x_init)
					start_angle_y = start_angle_y + (y_init - y_root[i])
					start_angle = start_angle + math.atan2(start_angle_y,start_angle_x)
				start_angle = start_angle/end

				tip_angle_x = x_root[length_x_root-1] - x_init
				tip_angle_y = y_init - y_root[length_x_root-1]
				tip_angle = math.atan2(tip_angle_y,tip_angle_x)

				total_start_angle = 0
				maxi_start_angle = start_angle
				if start_angle - math.pi/2 >= 0:
					top_start_angle = start_angle - math.pi/2
					second_top_start_angle = -(2*math.pi + 1)
				else:
					top_start_angle = math.pi + 1
					second_top_start_angle = start_angle - math.pi/2
				mini_start_angle = start_angle
				
				total_tip_angle = 0
				maxi_tip_angle = tip_angle
				if tip_angle - math.pi/2 >= 0:
					top_tip_angle = tip_angle - math.pi/2
					second_top_tip_angle = -(2*math.pi + 1)
				else:
					top_tip_angle = math.pi + 1
					second_top_tip_angle = tip_angle - math.pi/2
				mini_tip_angle = tip_angle

				plant = root[1]
				counter_plant = 1
				counter_root_plant = 1
				counter_root = 1


			genotype = root[0]
			file_name = root[5]
		
		elif root [0] != genotype and counter_root == 0:
			genotype = ""

	if counter_root_plant != 1:
		if maxi_start_angle != -(math.pi + 1) and mini_start_angle != math.pi + 1 and maxi_start_angle != mini_start_angle:
			if top_start_angle != math.pi + 1 and second_top_start_angle != -(2*math.pi + 1):
				total_start_angle = total_start_angle + 2 * math.pi - (top_start_angle - second_top_start_angle)
			elif top_start_angle == math.pi + 1 or top_start_angle < 0:
				total_start_angle = total_start_angle + (maxi_start_angle - mini_start_angle)
		if maxi_tip_angle != -(math.pi + 1) and mini_tip_angle != math.pi + 1 and maxi_tip_angle != mini_tip_angle:
			if top_tip_angle != math.pi + 1 and second_top_tip_angle != -(2*math.pi + 1):
				total_tip_angle = total_tip_angle + 2 * math.pi - (top_tip_angle - second_top_tip_angle)
			elif top_tip_angle == math.pi + 1 or top_tip_angle < 0:
				total_tip_angle = total_tip_angle + (maxi_tip_angle - mini_tip_angle)
	else:
		total_start_angle = total_start_angle + abs(start_angle)
		total_tip_angle = total_tip_angle + abs(tip_angle)

	if Result == "P" and counter_plant != 0:
		total_start_angle = math.degrees(total_start_angle / counter_plant)
		total_tip_angle = math.degrees(total_tip_angle / counter_plant)

		root_number = float(counter_root)/float(counter_plant)
			
		data_angle.append ([genotype,root_number,total_start_angle,total_tip_angle,counter_plant])

	elif Result == "S" and counter_root_plant !=0:
		total_start_angle = math.degrees(total_start_angle)
		total_tip_angle = math.degrees(total_tip_angle)
		data_angle.append ([genotype,counter_plant,plant,counter_root_plant,total_start_angle,total_tip_angle])

	return data_angle

def get_elongation_data(data_length_young,data_length_old,data_angle_young,data_angle_old):
	data_elongation = []
	
	for i in range (0, len(data_length_young)):
		counter = 0
		length_young = data_length_young[i]
		angle_young = data_angle_young[i]
		length_old = data_length_old[0]
		angle_old = data_angle_old[0]
		while length_old[0] != length_young[0] and counter < len(data_length_old) - 1:
			counter = counter + 1
			length_old = data_length_old[counter]
			angle_old = data_angle_old[counter]

		if (counter != len(data_length_old) - 1) or (counter == len(data_length_old) - 1 and length_old[0] == length_young[0]):
			genotype = length_old[0]
			average_bonus_root = length_old[1] - length_young[1]
			average_elongation_total = length_old[2] - length_young[2]
			average_elongation = length_old[3] - length_young[3]
			average_elongation_long = length_old[4] - length_young[4]
			bonus_plant = length_old[5] - length_young[5]
			bonus_root = length_old[6] - length_young[6]
			elongation_total = length_old[7] - length_young[7]
			elongation_long = length_old[8] - length_young[8]
			bonus_seed_angle = angle_old[2] - angle_young[2]
			bonus_tip_angle = angle_old[3] - angle_young[3]
					
			data_elongation.append ([genotype,average_bonus_root,average_elongation_total,average_elongation,average_elongation_long,bonus_plant,bonus_root,elongation_total,elongation_long,bonus_seed_angle,bonus_tip_angle])
		
	return data_elongation

def create_germination_genotype(fl,Array):
	import os,sys
	genotype = ""
	counter = 0
	seed = []
	for j in range (0, len (Array)):
		Array_in = Array[j]
		replicate = Array_in[0]
		if replicate[:-2] != genotype and genotype != "":
			total_seed = sum(seed)
			average_seed = mean(seed)
			std_seed = std(seed,average_seed)
			fl.write(str(genotype) + "," + str(counter) + "," + str(average_seed) + "," + str(std_seed) + "," + str(total_seed) + "," + "\n")
			seed = []
			seed.append(Array_in[1])
			genotype = replicate[:-2]
			counter = 1
		elif genotype == "":
			genotype = replicate[:-2]
			counter = 1
			seed = []
			seed.append(Array_in[1])
		else:
			counter = counter + 1
			seed.append(Array_in[1])

	total_seed = sum(seed)
	average_seed = mean(seed)
	std_seed = std(seed,average_seed)
	fl.write(str(genotype) + "," + str(counter) + "," + str(average_seed) + "," + str(std_seed) + "," + str(total_seed) + "," + "\n")
	return fl

def create_data_genotype(fl,data_length,data_angle):
	import os,sys,math
	genotype = ""
	replicate_number = ""
	for j in range (0, len (data_length)):
		data_length_in = data_length[j]
		data_angle_in = data_angle[j]
		replicate = data_length_in[0]
		if replicate[:-2] != genotype and genotype != "":
			total_root = sum(root)
			total_length = sum(length)
			total_long_length = sum(long_length)
			average_root = mean(root)
			ste_root = std(root,average_root) / math.sqrt(counter_plant)
			average_length = mean(length)
			ste_length = std(length,average_length) / math.sqrt(counter_plant)
			average_plant_length = mean(plant_length)
			ste_plant_length = std(plant_length,average_plant_length) / math.sqrt(counter_plant)
			average_long_length = mean(long_length)
			ste_long_length = std(long_length,average_long_length) / math.sqrt(counter_plant)
			average_start_angle = mean(start_angle)
			ste_start_angle = std(start_angle,average_start_angle) / math.sqrt(counter_plant)
			average_tip_angle = mean(tip_angle)
			ste_tip_angle = std(tip_angle,average_tip_angle) / math.sqrt(counter_plant)
			fl.write(str(genotype) + "," + str(counter) + "," + str(average_root) + "," + str(ste_root) + "," + str(average_length) + "," + str(ste_length) + "," + str(average_plant_length) + "," + str(ste_plant_length) + "," + str(average_long_length) + "," + str(ste_long_length) + "," + str(average_start_angle) + "," + str(ste_start_angle) + "," + str(average_tip_angle) + "," + str(ste_tip_angle) + "," + str(counter_plant) + "," + str(total_root) + "," + str(total_length) + "," + str(total_long_length) + "\n")
			root = []
			length = []
			plant_length = []
			long_length = []
			start_angle = []
			tip_angle = []
			root.append(data_length_in[3])
			length.append(data_length_in[5])
			plant_length.append(data_length_in[4])
			long_length.append(data_length_in[6])
			start_angle.append(data_angle_in[4])
			tip_angle.append(data_angle_in[5])
			genotype = replicate[:-2]
			replicate_number = replicate [-2:]
			counter = 1
			counter_plant = 1
		elif genotype == "":
			genotype = replicate[:-2]
			replicate_number = replicate [-2:]
			counter = 1
			counter_plant = 1
			root = []
			length = []
			plant_length = []
			long_length = []
			start_angle = []
			tip_angle = []
			root.append(data_length_in[3])
			length.append(data_length_in[5])
			plant_length.append(data_length_in[4])
			long_length.append(data_length_in[6])
			start_angle.append(data_angle_in[4])
			tip_angle.append(data_angle_in[5])
		else:
			if replicate[-2:] != replicate_number:
				counter = counter + 1
				replicate_number = replicate [-2:]
			counter_plant = counter_plant + 1
			root.append(data_length_in[3])
			length.append(data_length_in[5])
			plant_length.append(data_length_in[4])
			long_length.append(data_length_in[6])
			start_angle.append(data_angle_in[4])
			tip_angle.append(data_angle_in[5])
			
	total_root = sum(root)
	total_length = sum(length)
	total_long_length = sum(long_length)
	average_root = mean(root)
	ste_root = std(root,average_root) / math.sqrt(counter_plant)
	average_length = mean(length)
	ste_length = std(length,average_length) / math.sqrt(counter_plant)
	average_plant_length = mean(plant_length)
	ste_plant_length = std(plant_length,average_plant_length) / math.sqrt(counter_plant)
	average_long_length = mean(long_length)
	ste_long_length = std(long_length,average_long_length) / math.sqrt(counter_plant)
	average_start_angle = mean(start_angle)
	ste_start_angle = std(start_angle,average_start_angle) / math.sqrt(counter_plant)
	average_tip_angle = mean(tip_angle)
	ste_tip_angle = std(tip_angle,average_tip_angle) / math.sqrt(counter_plant)
	fl.write(str(genotype) + "," + str(counter) + "," + str(average_root) + "," + str(ste_root) + "," + str(average_length) + "," + str(ste_length) + "," + str(average_plant_length) + "," + str(ste_plant_length) + "," + str(average_long_length) + "," + str(ste_long_length) + "," + str(average_start_angle) + "," + str(ste_start_angle) + "," + str(average_tip_angle) + "," + str(ste_tip_angle) + "," + str(counter_plant) + "," + str(total_root) + "," + str(total_length) + "," + str(total_long_length) + "\n")
	return fl

def create_elongation_genotype(fl,data_elongation):
	import os,sys,math
	genotype = ""
	bonus_plant = 0
	for j in range (0, len (data_elongation)):
		data_elongation_in = data_elongation[j]
		replicate = data_elongation_in[0]
		if replicate[:-2] != genotype and genotype != "" and bonus_plant == 0:
			average_bonus_root = mean(bonus_root)
			ste_bonus_root = std(bonus_root,average_bonus_root) / math.sqrt(counter)
			average_elongation_total = mean(elongation_total)
			ste_elongation_total = std(elongation_total,average_elongation_total) / math.sqrt(counter)
			average_elongation_long = mean(elongation_long)
			ste_elongation_long = std(elongation_long,average_elongation_long) / math.sqrt(counter)
			average_bonus_seed_angle = mean(bonus_seed_angle)
			ste_bonus_seed_angle = std(bonus_seed_angle,average_bonus_seed_angle) / math.sqrt(counter)
			average_bonus_tip_angle = mean(bonus_tip_angle)
			ste_bonus_tip_angle = std(bonus_tip_angle,average_bonus_tip_angle) / math.sqrt(counter)
			fl.write(str(genotype) + "," + str(counter) + "," + str(average_bonus_root) + "," + str(ste_bonus_root) + "," + str(average_elongation_total) + "," + str(ste_elongation_total) + "," + str(average_elongation_long) + "," + str(ste_elongation_long) + "," + str(average_bonus_seed_angle) + "," + str(ste_bonus_seed_angle) + "," + str(average_bonus_tip_angle) + "," + str(ste_bonus_tip_angle) + "\n")
			bonus_root = []
			elongation_total = []
			elongation_long = []
			bonus_seed_angle = []
			bonus_tip_angle = []
			bonus_plant = data_elongation_in[5]
			bonus_root.append(data_elongation_in[6])
			elongation_total.append(data_elongation_in[7])
			elongation_long.append(data_elongation_in[8])
			bonus_seed_angle.append(data_elongation_in[9])
			bonus_tip_angle.append(data_elongation_in[10])
			genotype = replicate[:-2]
			counter = 1
		elif genotype == "" or (replicate[:-2] != genotype and genotype != "" and bonus_plant != 0):
			genotype = replicate[:-2]
			counter = 1
			bonus_root = []
			elongation_total = []
			elongation_long = []
			bonus_seed_angle = []
			bonus_tip_angle = []
			bonus_plant = data_elongation_in[5]
			bonus_root.append(data_elongation_in[6])
			elongation_total.append(data_elongation_in[7])
			elongation_long.append(data_elongation_in[8])
			bonus_seed_angle.append(data_elongation_in[9])
			bonus_tip_angle.append(data_elongation_in[10])
		else:
			counter = counter + 1
			bonus_plant = bonus_plant + data_elongation_in[5]
			bonus_root.append(data_elongation_in[6])
			elongation_total.append(data_elongation_in[7])
			elongation_long.append(data_elongation_in[8])
			bonus_seed_angle.append(data_elongation_in[9])
			bonus_tip_angle.append(data_elongation_in[10])

	average_bonus_root = mean(bonus_root)
	ste_bonus_root = std(bonus_root,average_bonus_root) / math.sqrt(counter)
	average_elongation_total = mean(elongation_total)
	ste_elongation_total = std(elongation_total,average_elongation_total) / math.sqrt(counter)
	average_elongation_long = mean(elongation_long)
	ste_elongation_long = std(elongation_long,average_elongation_long) / math.sqrt(counter)
	average_bonus_seed_angle = mean(bonus_seed_angle)
	ste_bonus_seed_angle = std(bonus_seed_angle,average_bonus_seed_angle) / math.sqrt(counter)
	average_bonus_tip_angle = mean(bonus_tip_angle)
	ste_bonus_tip_angle = std(bonus_tip_angle,average_bonus_tip_angle) / math.sqrt(counter)
	fl.write(str(genotype) + "," + str(counter) + "," + str(average_bonus_root) + "," + str(ste_bonus_root) + "," + str(average_elongation_total) + "," + str(ste_elongation_total) + "," + str(average_elongation_long) + "," + str(ste_elongation_long) + "," + str(average_bonus_seed_angle) + "," + str(ste_bonus_seed_angle) + "," + str(average_bonus_tip_angle) + "," + str(ste_bonus_tip_angle) + "\n")
	
	return fl

def mean(data):
	n = len(data)
	mean = 0.0
	for i in range(0, n):
		mean = mean + data[i]
	mean = mean / n
	return mean

def std(data,mean):
	import math
	n = len(data)
	std = 0.0
	for i in range (0, n):
		std = std + (data[i] - mean)**2
	std = math.sqrt(std / n)
	return std

def create_data(age,Data,path):
	Result = "P"

	for i in range(0,len(Data)):
		Data_in = Data[i]
		fl = open (path + "\Picture_data_" + age + "_" + Data_in[0] +  ".csv", "w")

		pop_data = Data_in[1]

		data_length = get_length_data (pop_data,age,Result)
		data_angle = get_angle_data (pop_data,age,Result)

		fl.write("Genotype#Replicate,Average number of roots per seed,Average total root length,Average root length,Average length of the longest root,Average solid seed angle,Average solid tip angle,Number of germinated seeds,Total number of roots,Total root length,Total length of the longest roots\n")
		for i in range (0, len (data_length)):
			length_in = data_length[i]
			angle_in = data_angle[i]
			fl.write(str(length_in[0]) + "," + str(length_in[1]) + "," + str(length_in[2]) + "," + str(length_in[3]) + "," + str(length_in[4]) + "," + str(angle_in[2]) + "," + str(angle_in[3]) + "," + str(length_in[5]) + "," + str(length_in[6]) + "," + str(length_in[7]) + "," + str(length_in[8]) + "\n")

		fl.close()

	Result = "S"

	for i in range(0,len(Data)):
		Data_in = Data[i]

		pop_data = Data_in[1]

		data_length = get_length_data (pop_data,age,Result)
		data_angle = get_angle_data (pop_data,age,Result)
		
		seed_file = open(path + "\Raw_data_" + age + "_" + Data_in[0] +  ".csv", "w")
		
		seed_file.write("Genotype#Replicate,Plant number(program),Plant number(file),Number of roots,Total root length,Average root length,Length of the longest root,Solid seed angle,Solid tip angle\n")
		for i in range (0, len (data_length)):
			length_in = data_length[i]
			counter = 0
			angle_in = data_angle[counter]
			while (angle_in[0] != length_in[0] or angle_in[2] != length_in[2]) and counter < len (data_angle) - 1:
				counter = counter + 1
				angle_in = data_angle[counter]
			
			if (counter != len (data_angle) - 1) or (counter == len (data_angle) - 1 and (angle_in[0] == length_in[0] and angle_in[2] == length_in[2])):
				seed_file.write(str(length_in[0]) + "," + str(length_in[1]) + "," + str(length_in[2]) + "," + str(length_in[3]) + "," + str(length_in[4]) + "," + str(length_in[5]) + "," + str(length_in[6]) + "," + str(angle_in[4]) + "," + str(angle_in[5]) + "\n")
			else:
				seed_file.write(str(length_in[0]) + "," + str(length_in[1]) + "," + str(length_in[2]) + "," + str(length_in[3]) + "," + str(length_in[4]) + "," + str(length_in[5]) + "," + str(length_in[6]) + "," + "0" + "," + "0" + "\n")
			
		seed_file.close()
		
		fl = open (path + "\Genotype_data_" + age + "_" + Data_in[0] +  ".csv", "w")

		fl.write("Genotype,Number of replicate used,Average number of roots per seed,Standard error,Average root length,Standard error,Average total root length per seed,Standard error,Average length of the longest root per seed,Standard error,Average solid seed angle,Standard Error,Average solid tip angle,Standard error,Total number of germinated seeds,Total number of roots,Total root length,Total length of the longest roots\n")

		fl = create_data_genotype(fl,data_length,data_angle)

		fl.close()

def create_elongation_data(Data,path):
	Result = "P"
	
	for i in range(0,len(Data)):
		Data_in = Data[i]
		fl = open (path + "\Elongation_Picture_data_" + Data_in[0] +  ".csv", "w")
		
		pop_data = Data_in[1]
		
		data_length_young = get_length_data (pop_data,"young",Result)
		data_length_old = get_length_data (pop_data,"old",Result)
		data_angle_young = get_angle_data (pop_data,"young",Result)
		data_angle_old = get_angle_data (pop_data,"old",Result)
		
		data_elongation = get_elongation_data(data_length_young,data_length_old,data_angle_young,data_angle_old)

		fl.write("Genotype#Replicate,Average Increase of root number per seed,Average total elongation per seed,Average elongation,Average elongation of the longest root,Average evolution of solid seed angle,Average evolution of solid tip angle,Increase of germinated seeds number,Increase of root number,Total elongation,Total elongation of the longest roots\n")
		
		for i in range (0, len (data_elongation)):
			elongation_in = data_elongation[i]
			fl.write(str(elongation_in[0]) + "," + str(elongation_in[1]) + "," + str(elongation_in[2]) + "," + str(elongation_in[3]) + "," + str(elongation_in[4]) + "," + str(elongation_in[9]) + "," + str(elongation_in[10]) + "," + str(elongation_in[5]) + "," + str(elongation_in[6]) + "," + str(elongation_in[7]) + "," + str(elongation_in[8]) + "\n")
	
		fl.close()

		fl = open (path + "\Elongation_Genotype_data_" + Data_in[0] +  ".csv", "w")
		
		fl.write("Genotype,Number of replicates used,Increase of root number,Standard error,Average elongation per picture,Standard error,Average elongation of the longest root,Standard error,Average evolution of solid seed angle,Standard error,Average evolution of solid tip angle,Standard error\n")
		
		fl = create_elongation_genotype(fl,data_elongation)
		
		fl.close()
		
def picture_errors(path):
	import os, sys, fnmatch

	error_list = []

	for dirpath, dirs, files in os.walk(path):
		if dirpath != path:
			break
		else:
			for filename in fnmatch.filter(files, "Error*.csv"):
				file_path = os.path.join(dirpath, filename)
				split = file_path.split ('\\')
				n = len (split)
				file_name = split [n-1]
				split2 = file_name.split ('_')
				split2[5] = split2[5].replace(".csv","")
				spe = split2[4]
				pop = split2[5]
				criteria = split2[1] + "_" + split2[2]
				fl = open (file_path)
				for line in fl:
					line = line.replace("\n","")
					array = line.split(",")
					test = array[6]
					if test.isdigit() == True:
						if int(test) == 1:
							error_list.append([spe,pop,criteria,array[0]])
	return error_list

def check_errors():
	import os, sys, fnmatch

	path = "C:\\Users\\SD42489\\Desktop\\Projet\\"
	error_list = []

	for dirpath, dirs, files in os.walk(path):
		for filename in fnmatch.filter(files, "Check_errors*.csv"):
			file_path = os.path.join(dirpath, filename)
			#print file_path
			split = file_path.split ('\\')
			n = len (split)
			file_name = split [n-1]
			split2 = file_name.split ('_')
			split2[3] = split2[3].replace(".csv","")
			spe = split2[2]
			pop = split2[3]
			fl = open (file_path)
			for line in fl:
				line = line.replace("\n","")
				array = line.split(",")
				#print array
				error_list.append([spe,pop,array[0],array[1],array[2],array[3]])
	return error_list