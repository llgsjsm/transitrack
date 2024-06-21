import json
import heapq

# Load routes data from JSON file
with open('route.json') as f:
    data = json.load(f)
routes = data['routes']

def build_distance_map(routes):
    distance_map = {}
    for route in routes:
        from_station = route['from']
        to_station = route['to']
        distance = route['distance']
        
        if from_station not in distance_map:
            distance_map[from_station] = {}
        if to_station not in distance_map:
            distance_map[to_station] = {}
        
        distance_map[from_station][to_station] = distance
        distance_map[to_station][from_station] = distance  # Assuming bidirectional
    return distance_map

def heuristic(current, goal, distance_map):
    if current == goal:
        return 0
    if current not in distance_map or goal not in distance_map:
        return float('inf')
    
    return min(distance_map[current].values())

def build_graph(routes):
    graph = {}
    all_nodes = set()
    for route in routes:
        all_nodes.add(route['from'])
        all_nodes.add(route['to'])

    for node in all_nodes:
        graph[node] = {}

    for route in routes:
        graph[route['from']][route['to']] = (route['duration'], route['line'])
        graph[route['to']][route['from']] = (route['duration'], route['line'])  # Assuming bidirectional

    return graph, all_nodes

def a_star(graph, start, end, distance_map):
    open_list = []
    heapq.heappush(open_list, (0, start))
    came_from = {}
    g_score = {node: float('inf') for node in graph}
    g_score[start] = 0
    f_score = {node: float('inf') for node in graph}
    f_score[start] = heuristic(start, end, distance_map)

    while open_list:
        current = heapq.heappop(open_list)[1]

        if current == end:
            return reconstruct_path(came_from, current), g_score[end]

        for neighbor, (weight, line) in graph[current].items():
            tentative_g_score = g_score[current] + weight
            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = (current, line)
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, end, distance_map)
                if neighbor not in [i[1] for i in open_list]:
                    heapq.heappush(open_list, (f_score[neighbor], neighbor))

    return [], float('inf')  # Return an empty array if there's no path

def reconstruct_path(came_from, current):
    total_path = [current]
    total_lines = []
    while current in came_from:
        current, line = came_from[current]
        total_path.insert(0, current)
        total_lines.insert(0, line)
    return total_path, total_lines

# Build graph and distance map
graph, all_nodes = build_graph(routes)
distance_map = build_distance_map(routes)

# Take two inputs from the user
start = input("Enter the starting point: ")
end = input("Enter the end point: ")

# Calculate shortest path
(path, lines), total_duration = a_star(graph, start, end, distance_map)

if path:
    print(f"The shortest path between {start} and {end} is {total_duration} minutes.")
    print(f"The path is: {' -> '.join(path)}")

    for i in range(1, len(lines)):
        if lines[i] != lines[i - 1]:
            print(f"Changed from {lines[i - 1]} to {lines[i]} at {path[i]}")
else:
    print(f"There is no path from {start} to {end}.")
