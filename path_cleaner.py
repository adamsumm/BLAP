#Steps

#+ 1. grab all the files in the folder
#+ 2. for each file determine the domains blended
#+ 3. extract the interpolated "path"
#+ 4. store the starting location of said path (assume left to right, bottom to top)
#+ 5. convert the file to a file without paths
#6. run the agents for the given domains through the section with the appropriate params
#7. store the sequence of positions while doing this
# -- below here happens in C++ code
#8. compute the frechet distance between the interpolated - domain 1 - domain 2
#9. compute the mean and stdev of the frechet distances for each subset,





import glob
import json
import test_level_generalized as tlg
import os

domain_list = ["Castlevania", "Metroid", "Ninja Gaiden", "Mario", "MegaMan"]
jump_files = ["CV_Maps/Castlevania_estimated_jumps.json", "Metroid_Maps/Metroid_estimated_jumps.json", "NG_Maps/Ninja Gaiden_estimated_jumps.json", "SMB_Maps/SMB_estimated_jumps.json", "MM_Maps/Mega Man_estimated_jumps.json"]
path_chars = ['x', 'Ś', 'Ě', '+', 'ě', 'Ǩ', '★', '¦', '⌅', 'ѷ', '§', '©']
level_files = []
domains_per_level=[]
start_of_path = []
end_of_path = []

in_folder = "new_gru/gru_interpolation_256/"
path_folder="paths/"
geo_folder="geos/"

try:
	os.mkdir(in_folder+path_folder)
except OSError:
	pass

try:
	os.mkdir(in_folder+geo_folder)
except OSError:
	pass

l = os.listdir(in_folder) # dir is your directory path
number_files = len(l)

curr_file=1
for file in glob.glob(in_folder+"*.txt"):

	print(str(curr_file)+"/"+str(number_files))
	curr_file+=1
	file = file.replace(in_folder, '')
	level_files.append(file)
	domains = []
	#print(file)
	for d in domain_list:
		if d in file:
			domains.append(d)
	domains_per_level.append(domains)

	out = open(in_folder+path_folder+file+"_interpolated_path.txt", 'w')
	level = []
	level_geo = []
	with open(in_folder+file) as level_file:
		for line in level_file:
			level.append(line.rstrip())
			level_geo.append(line.rstrip())
	end_path =None
	for column in range(0, len(level[0])):
		for row in range(0,len(level)):
			if level[row][column] in path_chars:
				if len(start_of_path) < len(level_files):
					start_of_path.append([column, row])
				end_path = [column,row]
				out.write(str(column)+'\t'+str(row)+'\n')
				if level[row][column] == 'Ś':
					level_geo[row] = level_geo[row][:column]+'S'+level_geo[row][column+1:]
					continue
				elif level[row][column] == 'Ě':
					level_geo[row] = level_geo[row][:column]+'E'+level_geo[row][column+1:]
					continue
				elif level[row][column] == 'ě':
					level_geo[row] = level_geo[row][:column]+'e'+level_geo[row][column+1:]
					continue
				elif level[row][column] == '+':
					level_geo[row] = level_geo[row][:column]+'-'+level_geo[row][column+1:]
					continue
				elif level[row][column] == 'Ǩ':
					level_geo[row] = level_geo[row][:column]+'X'+level_geo[row][column+1:]
					continue
				elif level[row][column] == '★':
					level_geo[row] = level_geo[row][:column]+'*'+level_geo[row][column+1:]
					continue
				elif level[row][column] == '¦':
					level_geo[row] = level_geo[row][:column]+'|'+level_geo[row][column+1:]
					continue
				elif level[row][column] == '⌅':
					level_geo[row] = level_geo[row][:column]+'^'+level_geo[row][column+1:]
					continue
				elif level[row][column] == 'ѷ':
					level_geo[row] = level_geo[row][:column]+'v'+level_geo[row][column+1:]
					continue
				elif level[row][column] == '§':
					level_geo[row] = level_geo[row][:column]+'$'+level_geo[row][column+1:]
					continue
				elif level[row][column] == '©':
					level_geo[row] = level_geo[row][:column]+'o'+level_geo[row][column+1:]
					continue
	end_of_path.append(end_path)
	out.close()
	with open(in_folder+geo_folder+file+"_geo.txt",'w') as out_geo:
		for row in level_geo:
			out_geo.write(row+'\n')

	for d in domains:

		level_tmp = level_geo[:]

		jump_arcs = []
		if d == domain_list[0]:
			jump_arcs = json.load(open(jump_files[0]))['jumps']
		elif d == domain_list[1]:
			jump_arcs = json.load(open(jump_files[1]))['jumps']
		elif d == domain_list[2]:
			jump_arcs = json.load(open(jump_files[2]))['jumps']
		elif d == domain_list[3]:
			jump_arcs = json.load(open(jump_files[3]))['jumps']
		elif d == domain_list[4]:
			jump_arcs = json.load(open(jump_files[4]))['jumps']


		#load the tile descriptions
		tiles = json.load(open("general_tile_spec.json"))
		solid_tiles = tiles['solid']
		passable_tiles = tiles['passable']
		climbable_tiles = tiles['climbable']
		hazard_tiles = tiles['hazard']
	

		#y_offset = 0
		#x_offset = 0
		if 	len(start_of_path) == 0 or len(end_of_path) == 0 or \
			start_of_path[len(start_of_path)-1] == None or \
			end_of_path[len(end_of_path)-1] == None or \
			start_of_path[len(start_of_path)-1] == end_of_path[len(end_of_path)-1]:
			print("No path in level")
			#with open(in_folder+path_folder+file+"_"+d+"_path.txt","w") as path_file:
			#	path_file.write("\n")
		else:
			#print(len(start_of_path), len(end_of_path))
			#print("Start position: ",start_of_path[len(start_of_path)-1][0], start_of_path[len(start_of_path)-1][1])
			#print("Goal position: ",end_of_path[len(end_of_path)-1][0])
			path_found = tlg.testPlayability(in_folder+path_folder+file+"_"+d+"_annotated_path.txt",jump_arcs, solid_tiles, passable_tiles, climbable_tiles, hazard_tiles, level_tmp, 2, start_of_path[len(start_of_path)-1][0], start_of_path[len(start_of_path)-1][1], end_of_path[len(end_of_path)-1][0], None, False)
			#if no path found going to the right, try going to the left
			if path_found == 0:
				#print("Start position: ",end_of_path[len(end_of_path)-1][0], end_of_path[len(end_of_path)-1][1])
				#print("Goal position: ",start_of_path[len(start_of_path)-1][0])
				level_tmp = level_geo[:]
				path_found = tlg.testPlayability(in_folder+path_folder+file+"_"+d+"_annotated_path.txt",jump_arcs, solid_tiles, passable_tiles, climbable_tiles, hazard_tiles, level_tmp, 2, end_of_path[len(end_of_path)-1][0], end_of_path[len(end_of_path)-1][1], start_of_path[len(start_of_path)-1][0], None, False)
			with open(in_folder+path_folder+file+"_"+d+"_path.txt","w") as path_file:
				if path_found != 0:
					for p in path_found:
						path_file.write(str(p[0])+"\t"+str(p[1])+"\n")


		#print("Path found, ",path_found)
		#while path_found == 0:
		#	y_offset+=1
		#	if (start_of_path[len(start_of_path)-1][1] - y_offset) < 0:
		#		y_offset = 0
		#		x_offset+=1
		#	path_found = tlg.testPlayability(in_folder+path_folder+file+"_"+d+"_path.txt",jump_arcs, solid_tiles, passable_tiles, climbable_tiles, hazard_tiles, level_geo, 2, start_of_path[len(start_of_path)-1][0]+x_offset, start_of_path[len(start_of_path)-1][1]-y_offset, len(level_geo[0])-1, None, False)

with open(in_folder+"file_list.txt", "w") as fl:
	for f in level_files:
		fl.write(f+"\n")