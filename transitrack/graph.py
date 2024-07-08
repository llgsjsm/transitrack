import json
import heapq
from collections import deque

#import logging

# Set up logging (aaron)
# logging.basicConfig(level=logging.DEBUG, format='%(message)s')

def load_graph(file_name):
    with open(file_name) as f:
        data = json.load(f)
    graph = {}
    for edge in data["routes"]:
        from_station = edge["from"].strip().lower()
        to_station = edge["to"].strip().lower()
        
        if from_station not in graph:
            graph[from_station] = []
        if to_station not in graph:
            graph[to_station] = []
        
        graph[from_station].append({"to": to_station, "distance": edge["distance"], "duration": edge["duration"]})
        graph[to_station].append({"to": from_station, "distance": edge["distance"], "duration": edge["duration"]})
    return graph

def load_graph2(file_name):
    with open(file_name) as f:
        data = json.load(f)

    graph = {}
    all_nodes = set()
    
    for item in data['routes']:
        all_nodes.add(item['from'].strip().lower())
        all_nodes.add(item['to'].strip().lower())
    
    for node in all_nodes:
        graph[node] = {}
    
    for item in data['routes']:
        graph[item['from'].strip().lower()][item['to'].strip().lower()] = (item['duration'], item['line'])
        graph[item['to'].strip().lower()][item['from'].strip().lower()] = (item['duration'], item['line'])
    
    return graph, all_nodes

# def load_graph3(filename):
#     # load data from json file
#     with open(filename) as f:
#         data = json.load(f)

#     # transform data into graph, with edges and nodes for the calculations
#     graph = {}
#     all_nodes = set()
#     for item in data['routes']:
#         all_nodes.add(item['from'].strip().lower())
#         all_nodes.add(item['to'].strip().lower())

#     for node in all_nodes:
#         graph[node] = {}

#     # This part is different than load_graph2
#     for item in data['routes']:
#         graph[item['from'].strip().lower()][item['to'].strip().lower()] = (item['duration'], item['line'])
#         graph[item['to'].strip().lower()][item['from'].strip().lower()] = (item['duration'], item['line'])

#     # returns dictionary representing mrt network
#     return graph

#Sequential Search Algorithm (aaron)
def sequential_search(stations, query):
    results = []
    # logging.debug(f'Starting sequential search for query: {query}')
    for station in stations:
        # logging.debug(f'Checking station: {station}')
        if station.startswith(query):
            results.append(station)
            # logging.debug(f'Found match: {station}')
    # logging.debug(f'Search results: {results}')
    return results

#A* algorithm
def build_distance_map(graph):
    distance_map = {}
    for from_station, neighbors in graph.items():
        if from_station not in distance_map:
            distance_map[from_station] = {}
        for neighbor in neighbors:
            to_station = neighbor["to"]
            distance = neighbor["distance"]
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

        for neighbor in graph[current]:
            neighbor_node = neighbor["to"]
            weight = neighbor["duration"]
            tentative_g_score = g_score[current] + weight
            if tentative_g_score < g_score[neighbor_node]:
                came_from[neighbor_node] = current
                g_score[neighbor_node] = tentative_g_score
                f_score[neighbor_node] = g_score[neighbor_node] + heuristic(neighbor_node, end, distance_map)
                if neighbor_node not in [i[1] for i in open_list]:
                    heapq.heappush(open_list, (f_score[neighbor_node], neighbor_node))

    return [], float('inf')  # Return an empty array if there's no path

def reconstruct_path(came_from, current):
    total_path = [current]
    while current in came_from:
        current = came_from[current]
        total_path.insert(0, current)
    return total_path

def bfs(graph, start, end):
    queue = deque([(start, [start], [], 0)])  # (current_station, path, lines, total_duration)
    visited = set()

    while queue:
        current_station, path, lines, total_duration = queue.popleft()

        if current_station == end:
            return path, lines, total_duration # Assuming the fourth value is still needed for some reason

        visited.add(current_station)

        for neighbor, (duration, line) in graph[current_station].items():
            if neighbor not in visited and neighbor not in (node for node, _, _, _ in queue):
                new_path = path + [neighbor]
                new_lines = lines + [line] if line not in lines else lines  # Avoid duplicating lines
                new_total_duration = total_duration + duration
                queue.append((neighbor, new_path, new_lines, new_total_duration))

    return [], [], 0, 0

def bfs2(graph, start, end):
    # initialise the queue with the starting point and a path containing only the start
    queue = deque([(start, [start], [], 0, 0)])  # (current_station, path, lines, total_distance, total_duration)
    visited = set()

    while queue:
        # dequeue the first element in the queue
        current_station, path, lines, total_distance, total_duration = queue.popleft()

        # if the current station is the end station, return the path, lines, total distance, and total duration
        if current_station == end:
            return path, lines, total_distance, total_duration

        # mark the current station as visited
        visited.add(current_station)

        # explore all neighbors of the current station
        for neighbor, (distance, duration, line) in graph[current_station].items():
            if neighbor not in visited and neighbor not in (node for node, _, _, _, _ in queue):
                # append the neighbor to the path and line to lines
                new_path = path + [neighbor]
                new_lines = lines + [line]
                new_total_distance = total_distance + distance
                new_total_duration = total_duration + duration
                queue.append((neighbor, new_path, new_lines, new_total_distance, new_total_duration))

    # return empty lists and zeros if there is no path between the start and end
    return [], [], 0, 0

#dijkstras algorithm
def dijkstras(graph, starting_vertex, end_vertex, all_nodes):

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
    while pq:
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


#DFS Algorithm
def dfs(graph, start, end):
    path = []
    journey = set()
    found = False
    total_duration = 0
    
    def dfs(node, current_duration):
        nonlocal found, total_duration
        if found:
            return
        if node == end:
            path.append(node)
            total_duration = current_duration
            found = True
            return
        journey.add(node)
        for next_station in graph[node]:
            if next_station["to"] not in journey:
                path.append(node)
                dfs(next_station["to"], current_duration + next_station["duration"])
                if found:
                    return
                path.pop()
        journey.remove(node)
    dfs(start, 0)
    if found:
        path.append(end)  # Append the end station to the path
        return path, total_duration
    else:
        return None, float('inf')
