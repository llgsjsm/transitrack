import json

def load_routes(file_name):
    with open(file_name) as f:
        data = json.load(f)
        return data['routes']
    
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