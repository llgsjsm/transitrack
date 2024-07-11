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
        for neighbor_info in graph[current_station]:
            neighbor = neighbor_info["to"]
            distance = neighbor_info["distance"]
            duration = neighbor_info["duration"]
            
            if neighbor not in visited and neighbor not in (node for node, _, _, _, _ in queue):
                 # append the neighbor to the path
                new_path = path + [neighbor]
                new_total_distance = total_distance + distance
                new_total_duration = total_duration + duration
                queue.append((neighbor, new_path, lines, new_total_distance, new_total_duration))

    # return empty lists and zeros if there is no path between the start and end
    return [], [], 0, 0


#dijkstras algorithm
def dijkstras(graph, start, end):
    open_list = []
    heapq.heappush(open_list, (0, start))  # Priority queue with (distance, node)
    came_from = {}  # To reconstruct the path
    g_score = {node: float('inf') for node in graph}  # Distance from start to node
    g_score[start] = 0  # Distance from start to itself is 0

    while open_list:
        current_distance, current_node = heapq.heappop(open_list)

        if current_node == end:
            return reconstruct_path(came_from, current_node), g_score[end]

        for neighbor in graph[current_node]:
            neighbor_node = neighbor["to"]
            weight = neighbor["duration"]
            tentative_g_score = g_score[current_node] + weight

            if tentative_g_score < g_score[neighbor_node]:
                came_from[neighbor_node] = current_node
                g_score[neighbor_node] = tentative_g_score
                if neighbor_node not in [i[1] for i in open_list]:
                    heapq.heappush(open_list, (g_score[neighbor_node], neighbor_node))

    return [], float('inf')  # Return an empty path and infinite distance if no path is found


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
