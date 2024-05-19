import json
import heapq

# Explanations here ok!:
# Djikstra is the discovery of edges/neighbors with the weight/cost as the distance
# heapq allows the heap queue algorithm to be used in Python - to enable Djikstra's algorithm
# json is used to load the data from the JSON file
# https://www.geeksforgeeks.org/python-program-for-dijkstras-shortest-path-algorithm-greedy-algo-7/
# https://www.udacity.com/blog/2021/10/implementing-dijkstras-algorithm-in-python.html
# https://github.com/arnab132/Dijkstras-Algorithm-Python
 
# calculate_shortest_path function - calculate the shortest path between 2 points (literally Djikstra's algorithm xd)
def calculate_shortest_path(graph, starting_vertex, end_vertex, all_nodes):

    # 1. Initialise distances and previous_nodes dictionaries
    # distances are set to infinity for all nodes except the STARTING node, (since they have their own 'cost' [which is the disntance in this case])
    distances = {vertex: float('infinity') for vertex in all_nodes}
    distances[starting_vertex] = 0

    # previous_nodes & previous_lines are set to None for all nodes
    # previous_nodes will store the previous node in the shortest path
    # previous_lines will store the MRT line
    previous_nodes = {vertex: None for vertex in all_nodes}
    previous_lines = {vertex: None for vertex in all_nodes}

    # 2. Implementation of Djikstra's algorithm
    # Starting will be init as 0
    pq = [(0, starting_vertex)]
    
    # While pq is not empty, (dist, current_vertex) = heapq.heappop(pq)
    # continues until there are no more vertices to visit, line 29 takes the smallest in each iteration
    while len(pq) > 0:
        (dist, current_vertex) = heapq.heappop(pq)

        # checks if the current vertex is the end vertex (reached destination)
        # path and lines are reversed, since it is constructed from end to start. We want to print from start
        if current_vertex == end_vertex:
            path = []
            lines = []
            while current_vertex is not None:
                path.append(current_vertex)
                if previous_lines[current_vertex] is not None:
                    lines.append(previous_lines[current_vertex])
                current_vertex = previous_nodes[current_vertex]
            path = path[::-1]  # Reverse the path
            lines = lines[::-1]  # Reverse the lines
            return distances[end_vertex], path, lines

        # checks if distance is greater than the current vertex
        if dist > distances[current_vertex]:
            continue

        # !!! core Djikstra's - for each neighbor of the current vertex, calculate the new distance !!!
        # checks if the neighbor cost is less than the current cost, if so, update the distance
        for neighbor, (weight, line) in graph[current_vertex].items():
            old_distance = distances[neighbor]
            new_distance = dist + weight

            # if the new distance is less than the old distance, update the distance
            # update the previous node and line too
            if new_distance < old_distance:
                distances[neighbor] = new_distance
                previous_nodes[neighbor] = current_vertex
                previous_lines[neighbor] = line
                heapq.heappush(pq, (new_distance, neighbor))

    return distances[end_vertex], [], []

# Load data from JSON file
with open('route.json') as f:
    data = json.load(f)

# 3. Transform data into graph, with edges and nodes for the calculations
graph = {}
all_nodes = set()
for item in data['routes']:
    all_nodes.add(item['from'])
    all_nodes.add(item['to'])
# print("[DEBUG] Nodes: \n", all_nodes)

for node in all_nodes:
    graph[node] = {}
# print("[DEBUG] Graph: \n", graph)

for item in data['routes']:
    graph[item['from']][item['to']] = (item['duration'], item['line'])  # Add edge in one direction with line info
    graph[item['to']][item['from']] = (item['duration'], item['line'])  # Add edge in opposite direction with line info
print("[DEBUG] Graph with edges: \n", graph)

# Take two inputs from the user
start = input("Enter the starting point: ")
end = input("Enter the end point: ")

# Calculate shortest path
shortest_path, path, lines = calculate_shortest_path(graph, start, end, all_nodes)

if shortest_path == float('infinity'):
    print(f"There is no path between {start} and {end}.")
else:
    print(f"The shortest path between {start} and {end} is {shortest_path} minutes.")
    print(f"The path is: {' -> '.join(path)}")

    print("\n")
    for i in range(1, len(lines)):
        if lines[i] != lines[i-1]:
            print(f"Changed from {lines[i-1]} to {lines[i]} at {path[i]}")