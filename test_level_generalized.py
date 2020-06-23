#Tile-level Jump Automata agent
#=======================================================
#
# The Generator needs:
#
# + 1. 	To accept a generated jump arc file as input (json of jump arcs)
# + 2. 	To accept a tile specification file as input (json of solids, passables)
#	3.	To accept start and end positions as goals (or regions of positions?)
#	4.	To work for both vertical and horizontal level orientations, as well as mixed orientations
#	5.	To output the top N paths
#	6.	To output an annotated path through the provided level

import pathfinding
import argparse
import json

parser = argparse.ArgumentParser(description='Generate a set of jump arcs.')
parser.add_argument('--jumpfile', type=str, default='Kid Icarus_estimated_jumps.json',
					help='The name of the json file containing the possible jump arcs')
parser.add_argument('--tilefile', type=str, default='KI_tile_specs.json',
					help='The name of the json file containing the description of the \
					different tile types (solids, passable)')
parser.add_argument('--levelfile', type=str, default='kidicarus_1.txt',
					help='The name of the file containing the level to be tested')
parser.add_argument('--goalheight', type=int, default=None,
					help='The desired height the agent must reach to complete the level. \
					Note that numbers start from the top of the level and go down\
					If both goalheight and goalwidth are specified, then the exact position\
					 must be reached. \'None\' indicates no preference.\
					 A negative number indicates distance from the bottom of the level')
parser.add_argument('--goalwidth', type=int, default=None,
					help='The desired height the agent must reach to complete the level. \
					Note that numbers start from the left of the level and go right\
					If both goalheight and goalwidth are specified, then the exact position\
					 must be reached. \'None\' indicates no preference.\
					 A negative number indicated a distance from the right side of the level')
parser.add_argument('--startheight', type=int, default=-3,
					help='The starting height position of the agent;\
					Note that numbers start from the top of the level and go down\
					a negative number indicates starting at a distance from the bottom of the level')
parser.add_argument('--startwidth', type=int, default=5,
					help='The starting width position of the agent;\
					Note that numbers start from the left of the level and go right\
					a negative number indicates starting at a distance from the right side of the level')
parser.add_argument('--mode', type=int, default=1,
					help='Indicates what you want the agent to do for the given level:\
					1: find a single path through the level, and create an annotated level file\
					2: find the top n paths through the level\
					3: find the top n paths through the level and output the level with annotated paths\
					4: return how close the agent was able to get to the goal (distance from goal)')
parser.add_argument('--n', type=int, default=1,
					help='If modes 2-3 are chosen, this is the number of paths to find;\
					 otherwise it is not used.')
parser.add_argument('--levelwraps', type=bool, default=True,
					help='Indicates whether the level wraps around horizontally (e.g., whether the\
					player move off the right side of the screen and emerge on the left)')

parser.add_argument('--levelwrap', dest='level_wrap', action='store_true')
parser.add_argument('--no-levelwrap', dest='level_wrap', action='store_false')
parser.set_defaults(level_wrap=True)


def makeIsSolid(solids):
	def isSolid(tile):
		return tile in solids
	return isSolid

def makeIsPassable(passables, hazards):
	def isPassable(tile):
		return tile in passables and tile not in hazards
	return isPassable

def makeIsHazard(hazards):
	def isHazard(tile):
		return tile in hazards
	return isHazard

def makeIsClimbable(climbables):
	def isClimbable(tile):
		return tile in climbables
	return isClimbable

#Make sure we are getting the proper neighbors and that all checks are happending appropriately
def makeGetNeighbors(jumps,levelStr,visited,isSolid,isPassable,isClimbable,isHazard,level_wrap):
	maxX = len(levelStr[0])
	maxY = len(levelStr)-1
	jumpDiffs = []
	for jump in jumps:
		jumpDiff = [jump[0]]
		for ii in range(1,len(jump)):
			jumpDiff.append((jump[ii][0]-jump[ii-1][0],jump[ii][1]-jump[ii-1][1]))
		jumpDiffs.append(jumpDiff)
	jumps = jumpDiffs

	def getNeighbors(pos):
		dist = pos[0]-pos[2] 
		pos = pos[1] 
		visited.add((pos[0],pos[1])) 
		below = (pos[0],pos[1]+1) 

		neighbors = []
		#if the player falls to the bottom of the level
		if below[1] > maxY or isHazard(levelStr[below[1]][below[0]]):
			return []
		if pos[2] != -1:
			ii = pos[3] +1
			jump = pos[2]

			if ii < len(jumps[jump]):

				if level_wrap:
					if  (pos[1]+jumps[jump][ii][1] >= 0) and (not isSolid(levelStr[pos[1]+jumps[jump][ii][1]][(pos[0]+pos[4]*jumps[jump][ii][0])%maxX]) or isPassable((levelStr[pos[1]+jumps[jump][ii][1]][(pos[0]+pos[4]*jumps[jump][ii][0])%maxX]))):
						neighbors.append([dist+1,((pos[0]+pos[4]*jumps[jump][ii][0])%maxX,pos[1]+jumps[jump][ii][1],jump,ii,pos[4])])
						#print("mid jump")
					if 	pos[1]+jumps[jump][ii][1] < 0 and (not isSolid(levelStr[pos[1]+jumps[jump][ii][1]][(pos[0]+pos[4]*jumps[jump][ii][0])%maxX]) or isPassable(levelStr[pos[1]+jumps[jump][ii][1]][(pos[0]+pos[4]*jumps[jump][ii][0])%maxX])):
						neighbors.append([dist+1,((pos[0]+pos[4]*jumps[jump][ii][0])%maxX,0,jump,ii,pos[4])])
						#print("mid fall")
				else:
					if  pos[1]+jumps[jump][ii][1] >= 0 and (pos[0]+pos[4]*jumps[jump][ii][0]) < maxX and (pos[0]+pos[4]*jumps[jump][ii][0]) >= 0 and (not isSolid(levelStr[pos[1]+jumps[jump][ii][1]][(pos[0]+pos[4]*jumps[jump][ii][0])]) or  isPassable((levelStr[pos[1]+jumps[jump][ii][1]][(pos[0]+pos[4]*jumps[jump][ii][0])]))):
						neighbors.append([dist+1,((pos[0]+pos[4]*jumps[jump][ii][0]),pos[1]+jumps[jump][ii][1],jump,ii,pos[4])])
						#print("mid jump")
					if 	pos[1]+jumps[jump][ii][1] < 0 and (pos[0]+pos[4]*jumps[jump][ii][0]) < maxX and (pos[0]+pos[4]*jumps[jump][ii][0]) >= 0 and (not isSolid(levelStr[pos[1]+jumps[jump][ii][1]][pos[0]+pos[4]*jumps[jump][ii][0]]) or isPassable(levelStr[pos[1]+jumps[jump][ii][1]][(pos[0]+pos[4]*jumps[jump][ii][0])])):
						neighbors.append([dist+1,(pos[0]+pos[4]*jumps[jump][ii][0],0,jump,ii,pos[4])])
						#print("mid fall")
				
		if isSolid(levelStr[below[1]][below[0]]) and not isHazard(levelStr[below[1]][below[0]]):
			if level_wrap:
				if not isSolid(levelStr[pos[1]][(pos[0]+1)%maxX]):
					neighbors.append([dist+1,((pos[0]+1)%maxX,pos[1],-1)])
					#print("move right")
				if not isSolid(levelStr[pos[1]][(pos[0]-1)%maxX]):
					neighbors.append([dist+1,((pos[0]-1)%maxX,pos[1],-1)])
					#print("move left")

				for jump in range(len(jumps)):
					ii = 0
					if pos[1] >= 0 and (not isSolid(levelStr[pos[1]+jumps[jump][ii][1]][(pos[0]+jumps[jump][ii][0])%maxX]) or isPassable(levelStr[pos[1]+jumps[jump][ii][1]][(pos[0]+jumps[jump][ii][0])%maxX])):
						neighbors.append([dist+ii+1,((pos[0]+jumps[jump][ii][0])%maxX,pos[1]+jumps[jump][ii][1],jump,ii,1)])
						#print("start jump right")

					if pos[1] >= 0 and (not isSolid(levelStr[pos[1]+jumps[jump][ii][1]][(pos[0]-jumps[jump][ii][0])%maxX]) or isPassable(levelStr[pos[1]+jumps[jump][ii][1]][(pos[0]-jumps[jump][ii][0])%maxX])):
						neighbors.append([dist+ii+1,((pos[0]-jumps[jump][ii][0])%maxX,pos[1]+jumps[jump][ii][1],jump,ii,-1)])
						#print("start jump left")
			else:
				if pos[0]+1 < maxX and not isSolid(levelStr[pos[1]][(pos[0]+1)]):
					neighbors.append([dist+1,((pos[0]+1),pos[1],-1)])
					#print("move right")
				if pos[0]-1 >= 0 and not isSolid(levelStr[pos[1]][(pos[0]-1)]):
					neighbors.append([dist+1,((pos[0]-1),pos[1],-1)])
					#print("move left")

				for jump in range(len(jumps)):
					ii = 0

					#print(pos[1]+jumps[jump][ii][1], pos[0]-jumps[jump][ii][0], len(levelStr), len(levelStr[0]))
					#print(levelStr[pos[1]+jumps[jump][ii][1]])
					#print(isSolid(levelStr[pos[1]+jumps[jump][ii][1]][pos[0]-jumps[jump][ii][0]]))
					#print(isPassable(levelStr[pos[1]+jumps[jump][ii][1]][(pos[0]-jumps[jump][ii][0])]))

					if (pos[1] >= 0 and (pos[0]+jumps[jump][ii][0]) < maxX and (pos[0]+jumps[jump][ii][0]) >=0) and (not isSolid(levelStr[pos[1]+jumps[jump][ii][1]][pos[0]+jumps[jump][ii][0]]) or isPassable(levelStr[pos[1]+jumps[jump][ii][1]][pos[0]+jumps[jump][ii][0]])):
						neighbors.append([dist+ii+1,(pos[0]+jumps[jump][ii][0],pos[1]+jumps[jump][ii][1],jump,ii,1)])
						#print("start jump right")

					if (pos[1] >= 0 and (pos[0]-jumps[jump][ii][0]) < maxX and (pos[0]-jumps[jump][ii][0]) >= 0) and (not isSolid(levelStr[pos[1]+jumps[jump][ii][1]][pos[0]-jumps[jump][ii][0]]) or isPassable(levelStr[pos[1]+jumps[jump][ii][1]][(pos[0]-jumps[jump][ii][0])])):
						neighbors.append([dist+ii+1,(pos[0]-jumps[jump][ii][0],pos[1]+jumps[jump][ii][1],jump,ii,-1)])

		if not isSolid(levelStr[below[1]][below[0]]) or isPassable(levelStr[below[1]][below[0]]):
			neighbors.append([dist+1,(pos[0],pos[1]+1,-1)])
			if level_wrap:
				if pos[1]+1 <= maxY:
					if not isSolid(levelStr[pos[1]+1][(pos[0]+1)%maxX]) or isPassable(levelStr[pos[1]+1][(pos[0]+1)%maxX]):
						neighbors.append([dist+1.4,((pos[0]+1)%maxX,pos[1]+1,-1)])
						#print("falling right")
					if not isSolid(levelStr[pos[1]+1][(pos[0]-1)%maxX]) or isPassable(levelStr[pos[1]+1][(pos[0]-1)%maxX]):
						neighbors.append([dist+1.4,((pos[0]-1)%maxX,pos[1]+1,-1)])
						#print("falling left")
					if not isSolid(levelStr[pos[1]+1][pos[0]]) or isPassable(levelStr[pos[1]+1][pos[0]]):
						neighbors.append([dist+1,(pos[0],pos[1]+1,-1)])
						#falling straight down
				if pos[1]+2 <= maxY:
					if (not isSolid(levelStr[pos[1]+2][(pos[0]+1)%maxX]) or isPassable(levelStr[pos[1]+2][(pos[0]+1)%maxX])) and (not isSolid(levelStr[pos[1]+1][(pos[0]+1)%maxX]) or isPassable(levelStr[pos[1]+1][(pos[0]+1)%maxX])):
						neighbors.append([dist+2,((pos[0]+1)%maxX,pos[1]+2,-1)])
						#print("falling right fast")
					if (not isSolid(levelStr[pos[1]+2][(pos[0]-1)%maxX]) or isPassable(levelStr[pos[1]+2][(pos[0]-1)%maxX])) and (not isSolid(levelStr[pos[1]+1][(pos[0]-1)%maxX]) or isPassable(levelStr[pos[1]+1][(pos[0]-1)%maxX])):
						neighbors.append([dist+2,((pos[0]-1)%maxX,pos[1]+2,-1)])
						#print("falling left fast")
				#	if (not isSolid(levelStr[pos[1]+2][pos[0]]) or isPassable(levelStr[pos[1]+2][pos[0]])) and (not isSolid(levelStr[pos[1]+1][pos[0]]) or isPassable(levelStr[pos[1]+1][pos[0]])):
				#		neighbors.append([dist+2,(pos[0],pos[1]+2,-1)])
						#falling straight down fast
			else:
				if pos[1]+1 <= maxY:
					if pos[0]+1 < maxX and (not isSolid(levelStr[pos[1]+1][pos[0]+1]) or isPassable(levelStr[pos[1]+1][pos[0]+1])):
						neighbors.append([dist+1.4,(pos[0]+1,pos[1]+1,-1)])
						#print("falling right")
					if pos[0]-1 >= 0 and (not isSolid(levelStr[pos[1]+1][pos[0]-1]) or isPassable(levelStr[pos[1]+1][pos[0]-1])):
						neighbors.append([dist+1.4,(pos[0]-1,pos[1]+1,-1)])
						#print("falling left")
					if not isSolid(levelStr[pos[1]+1][pos[0]]) or isPassable(levelStr[pos[1]+1][pos[0]]):
						neighbors.append([dist+1,(pos[0],pos[1]+1,-1)])
						#falling straight down
				if pos[1]+2 <= maxY:
					if pos[0]+1 < maxX and (not isSolid(levelStr[pos[1]+2][pos[0]+1]) or isPassable(levelStr[pos[1]+2][pos[0]+1])) and (not isSolid(levelStr[pos[1]+1][pos[0]+1]) or isPassable(levelStr[pos[1]+1][pos[0]+1])):
						neighbors.append([dist+2,(pos[0]+1,pos[1]+2,-1)])
						#print("falling right fast")
					if pos[0]-1 >= 0 and (not isSolid(levelStr[pos[1]+2][pos[0]-1]) or isPassable(levelStr[pos[1]+2][pos[0]-1])) and (not isSolid(levelStr[pos[1]+1][pos[0]-1]) or isPassable(levelStr[pos[1]+1][pos[0]-1])):
						neighbors.append([dist+2,(pos[0]-1,pos[1]+2,-1)])
						#print("falling left fast")
					#if (not isSolid(levelStr[pos[1]+2][pos[0]]) or isPassable(levelStr[pos[1]+2][pos[0]])) and (not isSolid(levelStr[pos[1]+1][pos[0]]) or isPassable(levelStr[pos[1]+1][pos[0]])):
					#	neighbors.append([dist+2,(pos[0],pos[1]+2,-1)])
						#falling straight down fast
		
		#if currently on a climbable tile, see if we can climb in any direction
		if isClimbable(levelStr[pos[1]][pos[0]]):
			
			#up
			if pos[1]+1 <=maxY and (isClimbable(levelStr[below[1]][below[0]]) or not isSolid(levelStr[below[1]][below[0]]) or isPassable(levelStr[below[1]][below[0]])):
				neighbors.append([dist+1, (pos[0], pos[1]+1,-1)])
			#down
			if pos[1]-1 >= 0 and (isClimbable(levelStr[pos[1]-1][pos[0]]) or not isSolid(levelStr[pos[1]-1][pos[0]]) or isPassable(levelStr[pos[1]-1][pos[0]])):
				neighbors.append([dist+1, (pos[0], pos[1]-1,-1)])

			if level_wrap:
				#left
				if isClimbable(levelStr[pos[1]][(pos[0]-1)%maxX]) or (not isSolid(levelStr[pos[1]][(pos[0]-1)%maxX]) or isPassable(levelStr[pos[1]][(pos[0]-1)%maxX])):
					neighbors.append([dist+1, ((pos[0]-1)%maxX, pos[1],-1)])
				#right
				if isClimbable(levelStr[pos[1]][(pos[0]+1)%maxX]) or (not isSolid(levelStr[pos[1]][(pos[0]+1)%maxX]) or isPassable(levelStr[pos[1]][(pos[0]+1)%maxX])):
					neighbors.append([dist+1, ((pos[0]+1)%maxX, pos[1],-1)])
			else:
				#left
				if pos[0]-1 >= 0 and (isClimbable(levelStr[pos[1]][pos[0]-1]) or not isSolid(levelStr[pos[1]][pos[0]-1]) or isPassable(levelStr[pos[1]][pos[0]-1])):
					neighbors.append([dist+1, (pos[0]-1, pos[1],-1)])
				#right
				if pos[0]+1 < maxX and (isClimbable(levelStr[pos[1]][pos[0]+1]) or not isSolid(levelStr[pos[1]][pos[0]+1]) or isPassable(levelStr[pos[1]][pos[0]+1])):
					neighbors.append([dist+1, (pos[0]+1, pos[1],-1)])


		return neighbors
	return getNeighbors

def goalReached(current_width, current_height, goal_width, goal_height):
	#If no goal specified
	if goal_height == None and goal_width == None:
		print("No goal specified; so we reached it!")
		return True
	#If only a horizontal goal
	elif goal_height == None and goal_width != None:
		#print(str(current_width)+ " "+str(goal_width))
		if current_width == goal_width:
			#print(current_width, goal_width)
			print("horizontal goal reached!")
			return True
		else:
			return False
	#If only a vertical goal
	elif goal_height != None and goal_width == None:
		if current_height == goal_height:
			print("vertical goal reached!")
			return True
		else:
			return False
	#If an exact positional goal
	elif goal_height != None and goal_width != None:
		if current_height == goal_height and current_width == goal_width:
			print("positional goal reached!")
			return True
		else:
			return False

def tileDistance(X_1, Y_1, X_2, Y_2):

	if X_2 == None:
		return abs(Y_2 - Y_1)
	elif Y_2 == None:
		return abs(X_2 - X_1)
	else:
		return abs(X_2 - X_1) + abs(Y_2 - Y_1)


def findPaths(subOptimal, solids, passables, climbables, hazards, jumps, levelStr, start_X, start_Y, goal_X, goal_Y, level_wrap):
	visited = set()
	isSolid = makeIsSolid(solids)
	isPassable = makeIsPassable(passables, hazards)
	isHazard = makeIsHazard(hazards)
	isClimbable = makeIsClimbable(climbables)
	getNeighbors = makeGetNeighbors(jumps,levelStr,visited,isSolid,isPassable,isClimbable,isHazard,level_wrap)
	paths = pathfinding.astar_shortest_path( (start_X, start_Y,-1), (goal_X, goal_Y), goalReached, getNeighbors, subOptimal, tileDistance)
	return [[ (p[0],p[1]) for p in path] for path in paths]

# def testingPlayability(Jfile, mapName, mode):
#	 import json
#	 levelFilename = mapName
#	 level = []
#	 with open(levelFilename) as level_file:
#		 for line in level_file:
#			 level.append(line.rstrip())
#	 with open(Jfile) as data_file:
#		 platformerDescription = json.load(data_file)
#	 maxX = len(level[0])
#	 minY = 2
#	 maxY = len(level)-3
#	 paths=[]
	
#	 #returns the furthest distance travelled by
#	 if mode == 2:
#		 while len(paths)==0 and minY<maxY:
#			 paths =  findPaths(1000,platformerDescription['solid'],platformerDescription['passable'],platformerDescription['jumps'], level, minY, maxY)
#			 minY = minY+1
#			 f = open(mapName+"_Annotated_Path.txt", 'w')
#			 if len(paths) == 0:
#				 continue
#			 #	return 0;
		
#			 for p in paths[0]:
#				 level[p[1]] = level[p[1]][:p[0]] + 'x' + level[p[1]][p[0]+1:];
#			 #f1.write(str(p[1][1]) +'\t' + str(p[1][0])+'\n')
			
#			 for r in level:
#				 f.write(r+'\n')

#			 f.close();
#			 #f1.close();
#			 if(paths[0][len(paths[0])-1][0]) >= len(level[0])-5:
#				 return 1
#			 else:
#				 return 0

#	 if mode == 1:
#		 while len(paths)==0 and minY < maxY:
#			 paths =  findPaths(10,platformerDescription['solid'],platformerDescription['passable'],platformerDescription['jumps'],level, minY, maxY)
#			 minY = minY+1
#			 #print(paths)
#			 if len(paths) > 0:
#				 return paths[0][len(paths[0])-1][1]
	
#	 if mode == 0:
#		 paths = findPaths(10,platformerDescription['solid'],platformerDescription['passable'],platformerDescription['jumps'],level, minY, maxY)
#		 #print(paths[0][len(paths[0])-1][1]) if paths else print(0)
#		 return paths[0][len(paths[0])-1][1] if paths else 0
#		 #return len(paths[0]) if paths else 0


# CHECK IF THE TILE BELOW IS A "KILL" TILE: [HAZARD, NULL]
def testPlayability(output_level, jump_arcs, solids, passables, climbables, hazards, level, mode, start_X, start_Y, goal_X, goal_Y, level_wrap):
	paths = findPaths(1000, solids, passables, climbables, hazards, jump_arcs, level, start_X, start_Y, goal_X, goal_Y, level_wrap)

	f = open(output_level, 'w')
	if len(paths) == 0:
		print("No path found")
		return 0
		
	for p in paths[0]:
		level[p[1]] = level[p[1]][:p[0]] + '+' + level[p[1]][p[0]+1:]
	
	for r in level:
		f.write(r+'\n')
	f.close();

	return paths[0]
	#return paths[0][len(paths[0])-1][1] if paths else 0




if __name__ == "__main__":
	args = parser.parse_args()

	#load the jump arcs
	jump_arcs = json.load(open(args.jumpfile))['jumps']

	#load the tile descriptions
	tiles = json.load(open(args.tilefile))
	solid_tiles = tiles['solid']
	passable_tiles = tiles['passable']
	climbable_tiles = tiles['climbable']
	hazard_tiles = tiles['hazard']

	#load the level to be tested
	level = []
	with open(args.levelfile) as level_file:
		for line in level_file:
			level.append(line.rstrip())

	start_X = args.startwidth
	start_Y = args.startheight
	if start_X != None and start_X < 0:
		start_X = len(level[0])+start_X
	if start_Y != None and start_Y < 0:
		start_Y = len(level)+start_Y

	goal_X = args.goalwidth
	goal_Y = args.goalheight
	if goal_X != None and goal_X < 0:
		goal_X = len(level[0])+goal_X
	if goal_Y != None and goal_Y < 0:
		goal_Y = len(level)+goal_Y


	testPlayability(args.levelfile[:-4]+"_Annotated_Path.txt",jump_arcs, solid_tiles, passable_tiles, climbable_tiles, hazard_tiles, level, 2, start_X, start_Y, goal_X, goal_Y, args.level_wrap)



	#testingPlayability(args.jumpfile, args.levelfile, args.mode)
	#import sys
	#import json
	#if len(sys.argv)  < 4:
	#	print 'Usage: {} <platformer json> <level text filename> <full level (0) or as far as can go (1)>'.format(sys.argv[0])
	#	exit()

#levelFilename = sys.argv[2]
#level = []
#   with open(levelFilename) as level_file:
#	   for line in level_file:
#		   level.append(line.rstrip())
#   with open(sys.argv[1]) as data_file:
#	   platformerDescription = json.load(data_file)
#   maxX = len(level[0])-1
#   paths=[]
	
	#returns the furthest distance travelled by
	#   if sys.argv[3] == '1':
	#   while len(paths)==0 and maxX > 0:
	#	   paths =  findPaths(10,platformerDescription['solid'],platformerDescription['jumps'],level, maxX)
	#	   maxX = maxX-1
	#	   if len(paths) > 0:
	#		   print paths[0][len(paths[0])-1][0]
	#		   maxX =0
	#
	#if sys.argv[3] == '0':
	#   paths = findPaths(10,platformerDescription['solid'],platformerDescription['jumps'],level, maxX)
#   print len(paths)
#
