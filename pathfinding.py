
from math import sqrt
from heapq import heappush, heappop

def astar_shortest_path(src, dest, isdst, adj,subOptimal, heuristic):
    dist = {}
    prev = {}
    dist[src] = 0
    prev[src] = None
    heap = [(dist[src], src,0)]

    all_positions=[]
    pathLength = float('inf')
    paths = []
    path = []
    while heap:
        node = heappop(heap)
        path.append(node)
        all_positions.append(node[1])
        #print(node[1])
        if isdst(node[1][0], node[1][1], dest[0], dest[1]):
            print("dest found")
            if node[0] < pathLength:
                pathLength = node[0]
                path = []
                nodeR = node[1]
                while nodeR:
                    path.append(nodeR)
                    nodeR = prev[nodeR]
                path.reverse()
                paths.append(path)
                #Added by Sam Snodgrass to speed up results, as I only need 1 path
                return paths
                continue
            elif node[0] > pathLength+subOptimal:
                print("in here somehow")
                break
            else:
                print("other here")
                path = []
                nodeR = node[1]
                while nodeR:
                    path.append(nodeR)
                    nodeR = prev[nodeR]
                path.reverse()
                paths.append(path)
                continue



        for next_node in adj(node):
            next_node[0] += heuristic(next_node[1][0], next_node[1][1], dest[0], dest[1])
            next_node.append(heuristic(next_node[1][0], next_node[1][1], dest[0], dest[1]))
            if next_node[1] not in dist or next_node[0] < dist[next_node[1]]:
                #print node[1],next_node[1],heuristic(next_node[1])
                #exit()

                dist[next_node[1]] = next_node[0]
                prev[next_node[1]] = node[1]
                heappush(heap, next_node)
                #paths.append(path)
    #print(len(paths)," path(s) found")
    #if len(paths) == 0:
    #    paths.append(all_positions)

    return paths
