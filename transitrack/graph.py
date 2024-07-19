import json
import heapq
from collections import deque
import time

# Helper function to load the graph from a JSON file
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

# Helper function for load_graph2
def load_graph2(file_name):
    with open(file_name) as f:
        data = json.load(f)
    
    graph = {}
    detailed_graph = {}
    for edge in data["routes"]:
        from_station = edge["from"].strip().lower()
        to_station = edge["to"].strip().lower()
        distance = edge["distance"]
        duration = edge["duration"]
        line = edge["line"]
        
        if from_station not in graph:
            graph[from_station] = []
        if to_station not in graph:
            graph[to_station] = []
        
        if from_station not in detailed_graph:
            detailed_graph[from_station] = {}
        if to_station not in detailed_graph:
            detailed_graph[to_station] = {}
        
        graph[from_station].append({"to": to_station, "distance": distance, "duration": duration})
        graph[to_station].append({"to": from_station, "distance": distance, "duration": duration})
        
        detailed_graph[from_station][to_station] = (distance, duration, line)
        detailed_graph[to_station][from_station] = (distance, duration, line)
    
    return graph, detailed_graph

#Sequential Search Algorithm: AARON
def sequential_search(stations, query):
    results = []
    #logging.debug(f"Starting sequential search for '{query}'")
    for station in stations:
        if station.startswith(query):
            results.append(station)
            #logging.debug(f"Sequential search found: {station}")
            
    #logging.debug(f"Sequential search results: {results}")
    return results

#Binary Search Algorithm: AARON
def sort_station(stations):
    return sorted(stations, key=lambda x: x.lower())

#Binary Search Algorithm: AARON
def binary_search(stations, query):
    sorted_stations = sort_station(stations)
    low = 0
    high = len(sorted_stations) - 1
    results = []

    #logging.debug(f"Starting binary search for '{query}'")

    while low <= high:
        mid = (low + high) // 2
        current_station = sorted_stations[mid]
        #logging.debug(f"Binary search checking mid index {mid}: {current_station}")

        if current_station.startswith(query):
            # Add the matching station
            results.append(current_station)
            #logging.debug(f"Binary search found: {current_station}")

            # Search for other matches to the left
            left = mid - 1
            while left >= 0 and sorted_stations[left].startswith(query):
                results.append(sorted_stations[left])
                #logging.debug(f"Binary search found to the left: {sorted_stations[left]}")
                left -= 1

            # Search for other matches to the right
            right = mid + 1
            while right < len(sorted_stations) and sorted_stations[right].startswith(query):
                results.append(sorted_stations[right])
                #logging.debug(f"Binary search found to the right: {sorted_stations[right]}")
                right += 1

            # All matches found, no need to continue binary search
            break
        elif query < current_station:
            high = mid - 1
            #logging.debug(f"Binary search moving left: low={low}, high={high}")
        else:
            low = mid + 1
            #logging.debug(f"Binary search moving right: low={low}, high={high}")

    #logging.debug(f"Binary search results: {results}")
    return results

#Helper function to build distance map for A* Algorithm: JAKE
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

# Heuristic function for A* Algorithm: JAKE
def heuristic(current, goal, distance_map):
    if current == goal:
        return 0
    if current not in distance_map or goal not in distance_map:
        return float('inf')
    
    return min(distance_map[current].values())

# A* Algorithm: JAKE
def a_star(graph, start, end, distance_map):
    start_time = time.perf_counter() # Start time

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
            end_time = time.perf_counter() # End time
            print(f"A* execution time: {end_time - start_time:.6f} seconds")
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
    
    end_time = time.perf_counter() # End time
    print(f"A* execution time: {end_time - start_time:.6f} seconds")
    return [], float('inf')  # Return an empty array if there's no path

# Helper function for A* Algorithm & Dijkstra's Algorithm: JAKE & HAZEL
def reconstruct_path(came_from, current):
    total_path = [current]
    while current in came_from:
        current = came_from[current]
        total_path.insert(0, current)
    return total_path

# Breadth-First Search Algorithm: RAUL
def bfs(graph, start, end):
    start_time = time.perf_counter()  # Start time

    # initialise the queue with the starting point and a path containing only the start
    queue = deque([(start, [start], [], 0, 0)])  # (current_station, path, lines, total_distance, total_duration)
    visited = set()

    while queue:
        # dequeue the first element in the queue
        current_station, path, lines, total_distance, total_duration = queue.popleft()

        # if the current station is the end station, return the path, lines, total distance, and total duration
        if current_station == end:
            end_time = time.perf_counter()  # End time
            print(f"BFS execution time: {end_time - start_time:.6f} seconds")
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

    end_time = time.perf_counter()  # End time
    print(f"BFS execution time: {end_time - start_time:.6f} seconds")
    # return empty lists and zeros if there is no path between the start and end
    return [], [], 0, 0

# Djikstras algorithm: HAZEL
def dijkstras(graph, start, end):
    start_time = time.perf_counter() # Start time

    open_list = []
    heapq.heappush(open_list, (0, start))  # Priority queue with (distance, node)
    came_from = {}  # To reconstruct the path
    g_score = {node: float('inf') for node in graph}  # Distance from start to node
    g_score[start] = 0  # Distance from start to itself is 0

    while open_list:
        current_distance, current_node = heapq.heappop(open_list)

        if current_node == end:
            end_time = time.perf_counter() # End time
            print(f"Dijkstra's execution time: {end_time - start_time:.6f} seconds")
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

    end_time = time.perf_counter()  # End time
    print(f"Dijkstra's execution time: {end_time - start_time:.6f} seconds")
    return [], float('inf')  # Return an empty path and infinite distance if no path is found

# Bellman-Ford Algorithm: RAUL
def bellman_ford(graph, start, end):
    start_time = time.perf_counter()  # Start time

    # step 1: initialise distances from start to all other stations as infinity and the predecessor of each station as None
    distance = {station: float('inf') for station in graph}
    predecessor = {station: None for station in graph}
    distance[start] = 0

    # step 2: relax all edges n - 1 times (n = number of vertices)
    for _ in range(len(graph) - 1):
        for station in graph:
            for edge in graph[station]:  # Iterate through the list of edges
                neighbor = edge["to"]
                weight = edge["distance"]
                duration = edge["duration"]
                if distance[station] + weight < distance[neighbor]:
                    distance[neighbor] = distance[station] + weight
                    predecessor[neighbor] = (station, weight, duration)

    # step 3: check for negative-weight cycles
    for station in graph:
        for edge in graph[station]:  # Iterate through the list of edges
            neighbor = edge["to"]
            weight = edge["distance"]
            duration = edge["duration"]
            if distance[station] + weight < distance[neighbor]:
                print("Graph contains a negative-weight cycle")
                return None, None
            
    end_time = time.perf_counter()  # End time
    print(f"Bellman-Ford execution time: {end_time - start_time:.6f} seconds")

    # if the end station is not reachable from the start station, return None
    if distance[end] == float('inf'):
        return None, None

    # construct the shortest path from start to end
    path = []
    total_distance = 0
    total_duration = 0
    current_station = end

    # trace the path from end to start using the predecessor dictionary
    while current_station is not None:
        path.append(current_station)  # add the current station to the path
        if predecessor[current_station] is not None:
            # retrieve the predecessor station, line, weight, and duration
            prev_station, weight, duration = predecessor[current_station]
            total_distance += weight  # add the distance to the total distance
            total_duration += duration  # add the duration to the total duration
        # move to the predecessor station
        current_station = predecessor[current_station][0] if predecessor[current_station] is not None else None

    # reverse the path and lines to get the correct order from start to end
    path.reverse()

    # return the final path, lines, total distance, and total duration
    return path, total_distance, total_duration

# Depth-First Search Algorithm: XEN
def dfs(graph, start, end):
    start_time = time.perf_counter()  # Start time

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

    end_time = time.perf_counter()  # End time
    print(f"DFS execution time: {end_time - start_time:.6f} seconds")

    if found:
        return path, total_duration
    else:
        return None, float('inf')

# Floyd-Warshall Algorithm: JAKE 
def floyd(duration_matrix, line_matrix):
    start_time = time.perf_counter()  # Start time

    n = len(duration_matrix)
    dist = [row[:] for row in duration_matrix]
    next_node = [[None] * n for _ in range(n)]
    
    for i in range(n):
        for j in range(n):
            if duration_matrix[i][j] != float('inf'):
                next_node[i][j] = j
    
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][j] > dist[i][k] + dist[k][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    next_node[i][j] = next_node[i][k]

    end_time = time.perf_counter()  # End time
    print(f"Floyd-Warshall execution time: {end_time - start_time:.6f} seconds")
    
    return dist, next_node

# Helper function for Floyd-Warshall Algorithm: JAKE
def reconstruct_path2(start, end, next_node, line_matrix, station_index, stations):
    path = []
    lines = []
    if next_node[station_index[start]][station_index[end]] is None:
        return path, lines
    
    current = station_index[start]
    while current != station_index[end]:
        path.append(stations[current])
        next_station = next_node[current][station_index[end]]
        lines.append(line_matrix[current][next_station])
        current = next_station
    
    path.append(end)
    return path, lines

# Bidirectional A* Algorithm: JAKE
def bidirectional_astar(graph, start, end, distance_map):
    start_time = time.perf_counter()  # Start time

    forward_open_list = []
    backward_open_list = []
    heapq.heappush(forward_open_list, (0, start))
    heapq.heappush(backward_open_list, (0, end))
    forward_came_from = {}
    backward_came_from = {}
    forward_g_score = {node: float('inf') for node in graph}
    backward_g_score = {node: float('inf') for node in graph}
    forward_g_score[start] = 0
    backward_g_score[end] = 0
    forward_f_score = {node: float('inf') for node in graph}
    backward_f_score = {node: float('inf') for node in graph}
    forward_f_score[start] = heuristic(start, end, distance_map)
    backward_f_score[end] = heuristic(end, start, distance_map)

    meeting_point = None

    while forward_open_list and backward_open_list:
        # Forward search
        if forward_open_list:
            current_forward = heapq.heappop(forward_open_list)[1]
            if current_forward in backward_came_from:
                meeting_point = current_forward
                break

            for neighbor in graph[current_forward]:
                neighbor_node = neighbor["to"]
                weight = neighbor["duration"]
                tentative_g_score = forward_g_score[current_forward] + weight
                if tentative_g_score < forward_g_score[neighbor_node]:
                    forward_came_from[neighbor_node] = current_forward
                    forward_g_score[neighbor_node] = tentative_g_score
                    forward_f_score[neighbor_node] = forward_g_score[neighbor_node] + heuristic(neighbor_node, end, distance_map)
                    if neighbor_node not in [i[1] for i in forward_open_list]:
                        heapq.heappush(forward_open_list, (forward_f_score[neighbor_node], neighbor_node))

        # Backward search
        if backward_open_list:
            current_backward = heapq.heappop(backward_open_list)[1]
            if current_backward in forward_came_from:
                meeting_point = current_backward
                break

            for neighbor in graph[current_backward]:
                neighbor_node = neighbor["to"]
                weight = neighbor["duration"]
                tentative_g_score = backward_g_score[current_backward] + weight
                if tentative_g_score < backward_g_score[neighbor_node]:
                    backward_came_from[neighbor_node] = current_backward
                    backward_g_score[neighbor_node] = tentative_g_score
                    backward_f_score[neighbor_node] = backward_g_score[neighbor_node] + heuristic(neighbor_node, start, distance_map)
                    if neighbor_node not in [i[1] for i in backward_open_list]:
                        heapq.heappush(backward_open_list, (backward_f_score[neighbor_node], neighbor_node))

    end_time = time.perf_counter()  # End time
    print(f"Bidirectional A* execution time: {end_time - start_time:.6f} seconds")

    if meeting_point is None:
        return [], float('inf')  # No path found

    forward_path = reconstruct_path(forward_came_from, meeting_point)
    backward_path = reconstruct_path(backward_came_from, meeting_point)
    total_path = forward_path + backward_path[::-1][1:]
    total_duration = forward_g_score[meeting_point] + backward_g_score[meeting_point]

    return total_path, total_duration

# Helper function to build distance matrix for Floyd-Warshall Algorithm: JAKE 
def build_distance_matrix(routes):
    stations = set()
    for route in routes:
        stations.add(route['from'])
        stations.add(route['to'])
    
    stations = list(stations)
    station_index = {station: idx for idx, station in enumerate(stations)}
    
    n = len(stations)
    duration_matrix = [[float('inf')] * n for _ in range(n)]
    line_matrix = [[None] * n for _ in range(n)]
    
    for i in range(n):
        duration_matrix[i][i] = 0  # Duration to self is zero
        line_matrix[i][i] = None   # No line needed for the same station
    
    for route in routes:
        from_idx = station_index[route['from']]
        to_idx = station_index[route['to']]
        duration = route['duration']
        line = route['line']
        
        duration_matrix[from_idx][to_idx] = duration
        duration_matrix[to_idx][from_idx] = duration  # Assuming bidirectional
        line_matrix[from_idx][to_idx] = line
        line_matrix[to_idx][from_idx] = line  # Assuming bidirectional
    
    return duration_matrix, line_matrix, station_index, stations

# Bidirectional Breadth-First Search Algorithm: RAUL
def bidirectional_bfs(graph, start, end):
    start_time = time.perf_counter()  # Start time

    if start == end:
        return [start], [], 0, 0

    forward_queue = deque([(start, [start], [], 0, 0)])
    backward_queue = deque([(end, [end], [], 0, 0)])

    forward_visited = {start: (start, [start], [], 0, 0)}
    backward_visited = {end: (end, [end], [], 0, 0)}

    while forward_queue and backward_queue:
        if forward_queue:
            current_station, path, lines, total_distance, total_duration = forward_queue.popleft()
            for neighbor, (distance, duration, line) in graph[current_station].items():
                if neighbor not in forward_visited:
                    new_path = path + [neighbor]
                    new_lines = lines + [line]
                    new_total_distance = total_distance + distance
                    new_total_duration = total_duration + duration
                    forward_visited[neighbor] = (neighbor, new_path, new_lines, new_total_distance, new_total_duration)
                    forward_queue.append((neighbor, new_path, new_lines, new_total_distance, new_total_duration))
                    if neighbor in backward_visited:
                        end_time = time.perf_counter()  # End time
                        print(f"Bidirectional BFS execution time: {end_time - start_time:.6f} seconds")
                        return combine_paths(forward_visited[neighbor], backward_visited[neighbor])

        if backward_queue:
            current_station, path, lines, total_distance, total_duration = backward_queue.popleft()
            for neighbor, (distance, duration, line) in graph[current_station].items():
                if neighbor not in backward_visited:
                    new_path = path + [neighbor]
                    new_lines = lines + [line]
                    new_total_distance = total_distance + distance
                    new_total_duration = total_duration + duration
                    backward_visited[neighbor] = (neighbor, new_path, new_lines, new_total_distance, new_total_duration)
                    backward_queue.append((neighbor, new_path, new_lines, new_total_distance, new_total_duration))
                    if neighbor in forward_visited:
                        end_time = time.perf_counter()  # End time
                        print(f"Bidirectional BFS execution time: {end_time - start_time:.6f} seconds")
                        return combine_paths(forward_visited[neighbor], backward_visited[neighbor])

    end_time = time.perf_counter()  # End time
    print(f"Bidirectional BFS execution time: {end_time - start_time:.6f} seconds")
    return [], [], 0, 0

# Helper function to combine paths from bidirectional BFS: RAUL
def combine_paths(forward, backward):
    _, forward_path, forward_lines, forward_distance, forward_duration = forward
    _, backward_path, backward_lines, backward_distance, backward_duration = backward
    
    combined_path = forward_path + backward_path[::-1][1:]
    combined_lines = forward_lines + backward_lines[::-1]
    combined_distance = forward_distance + backward_distance
    combined_duration = forward_duration + backward_duration
    
    return combined_path, combined_lines, combined_distance, combined_duration