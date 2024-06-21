import json

#default code to make graph for algorithm
with open("route.json", "r") as file:
    data = json.load(file)

def create_graph(data):
    graph = {}
    for edge in data["routes"]:
        if edge["from"] not in graph:
            graph[edge["from"]] = []
        if edge["to"] not in graph:
            graph[edge["to"]] = []
        graph[edge["from"]].append({"to": edge["to"], "distance": edge["distance"]})
        graph[edge["to"]].append({"to": edge["from"], "distance": edge["distance"]})
    return graph

graph = create_graph(data)

print("Graph adjacency list with distances:")
for node in graph:
    connections = ", ".join([f"{adj['to']}({adj['distance']}km)" for adj in graph[node]])
    print(f"{node}: {connections}")



#all the pathing available together with total distance
def find_all_paths(graph, start, end, path=[], total_distance=0):
    path = path + [(start, total_distance)]
    if start == end:
        return [path]
    if start not in graph:
        return []
    paths = []
    for node in graph[start]:
        if node["to"] not in [p[0] for p in path]: 
            newpaths = find_all_paths(graph, node["to"], end, path, total_distance + node["distance"])
            for newpath in newpaths:
                paths.append(newpath)
    return paths

#DFS pathing
def find_dfs_paths(graph, start, end):
    path = []
    journey = set()
    found = False
    
    def dfs(node):
        nonlocal found
        if found:
            return
        if node == end:
            path.append(node)
            found = True
            return
        journey.add(node)
        for next_station in graph[node]:
            if next_station["to"] not in journey:
                path.append(node)
                dfs(next_station["to"])
                if found:
                    return
                path.pop()
        journey.remove(node)
    dfs(start)
    if found:
        path.insert(0, start)  # Insert start station at the beginning of the path
        return path
    else:
        return None



start_station = "Tuas Link"
end_station = "Bartley"

#all_paths = find_all_paths(graph, start_station, end_station)
dfs_path = find_dfs_paths(graph, start_station, end_station)


#print all paths
#unique_paths = []
#for path in all_paths:
#    stations = " -> ".join([p[0] for p in path])
#    total_distance = path[-1][1]
#    if stations not in unique_paths:
#        unique_paths.append(stations)
#        print(f"Path: {stations}, Total distance: {total_distance}km")


#print DFS path
if dfs_path:
    stations = " -> ".join(dfs_path)
    print(f"\nFirst path from {start_station} to {end_station} using DFS:")
    print(f"Path: {stations}")
else:
    print(f"\nNo path found from {start_station} to {end_station} using DFS.")