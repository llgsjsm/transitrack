from flask import Flask, request, render_template, jsonify
from graph import load_graph, load_graph2, dfs, build_distance_map, a_star, dijkstras, sequential_search, bfs, bellman_ford, binary_search, bidirectional_bfs, bidirectional_astar, build_distance_matrix, floyd, reconstruct_path2
import requests
from flask_cors import CORS
import time
import json

app = Flask(__name__)
CORS(app)

stations = load_graph('static/route.json')
stations2, detailed_graph = load_graph2('static/route.json')
distance_map = build_distance_map(stations)  # Build distance map once
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/routeInfo/')
def get_routes():
    try:
        with open('static/route.json', 'r') as f:
            routes = json.load(f)
        return jsonify(routes), 200
    except FileNotFoundError:
        return jsonify({'error': 'Routes data file not found.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dfs/')
def api_dfs():
    try:
        req = request.args
        start = req.get('start').strip().lower()
        end = req.get('end').strip().lower()

        # Check if the start and end stations exist in the graph
        if start not in stations:
            return jsonify({'error': f'Start station {start} not found in the graph.'}), 400
        if end not in stations:
            return jsonify({'error': f'End station {end} not found in the graph.'}), 400

        path, total_duration = dfs(stations, start, end)
        if path is None:
            return jsonify({'route': 'null'}), 400
        else:
            return jsonify({'route': path, 'duration': total_duration}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/astar/')
def api_astar():
    try:
        req = request.args
        start = req.get('start').strip().lower()
        end = req.get('end').strip().lower()

        # Check if the start and end stations exist in the graph
        if start not in stations:
            return jsonify({'error': f'Start station {start} not found in the graph.'}), 400
        if end not in stations:
            return jsonify({'error': f'End station {end} not found in the graph.'}), 400

        path, total_duration = a_star(stations, start, end, distance_map)
        if not path:
            return jsonify({'route': 'null'}), 400
        else:
            return jsonify({'route': path, 'duration': total_duration}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bidirectional_astar/')
def api_bidirectional_a_star():
    try:
        req = request.args
        start = req.get('start').strip().lower()
        end = req.get('end').strip().lower()

        if start not in stations:
            return jsonify({'error': f'Start station {start} not found in the graph.'}), 400
        if end not in stations:
            return jsonify({'error': f'End station {end} not found in the graph.'}), 400

        path, total_duration = bidirectional_astar(stations, start, end, distance_map)
        
        if not path:
            return jsonify({'route': 'null'}), 400
        else:
            return jsonify({'route': path, 'duration': total_duration}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/djikstras/')
def api_djikstras():
    try:
        req = request.args
        start = req.get('start').strip().lower()
        end = req.get('end').strip().lower()
        
        # Check if the start and end stations exist in the graph
        if start not in stations:
            return jsonify({'error': f'Start station {start} not found in the graph.'}), 400
        if end not in stations:
            return jsonify({'error': f'End station {end} not found in the graph.'}), 400

        path, total_duration = dijkstras(stations, start, end)
        if not path:
            return jsonify({'route': 'null'}), 400
        else:
            return jsonify({'route': path, 'duration': total_duration}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bfs/')
def api_bfs():
    try:
        req = request.args
        start = req.get('start').strip().lower()
        end = req.get('end').strip().lower()

        # Check if the start and end stations exist in the graph
        if start not in stations:
            return jsonify({'error': f'Start station {start} not found in the graph.'}), 400
        if end not in stations:
            return jsonify({'error': f'End station {end} not found in the graph.'}), 400

        path, lines, total_distance, total_duration = bfs(stations, start, end)
        
        if not path:
            return jsonify({'route': 'null'}), 400
        else:
            return jsonify({'route': path, 'duration': total_duration}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/bidirectional_bfs/')
def api_bidirectional_bfs():
    try:
        req = request.args
        start = req.get('start').strip().lower()
        end = req.get('end').strip().lower()

        # Check if the start and end stations exist in the graph
        if start not in detailed_graph:
            return jsonify({'error': f'Start station {start} not found in the graph.'}), 400
        if end not in detailed_graph:
            return jsonify({'error': f'End station {end} not found in the graph.'}), 400

        path, lines, total_distance, total_duration = bidirectional_bfs(detailed_graph, start, end)

        if not path:
            return jsonify({'route': 'null'}), 400
        else:
            return jsonify({'route': path, 'lines': lines, 'distance': total_distance, 'duration': total_duration}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/floyd/')
def api_floyd():
    try:
        req = request.args
        start = req.get('start').strip().lower()
        end = req.get('end').strip().lower()

        if start not in detailed_graph:
            return jsonify({'error': f'Start station {start} not found in the graph.'}), 400
        if end not in detailed_graph:
            return jsonify({'error': f'End station {end} not found in the graph.'}), 400
        
        routes = []
        for from_station, connections in detailed_graph.items():
            for to_station, (distance, duration, line) in connections.items():
                routes.append({
                    'from': from_station,
                    'to': to_station,
                    'distance': distance,
                    'duration': duration,
                    'line': line
                })
        
        # Build the distance and line matrices for Floyd-Warshall
        duration_matrix, line_matrix, station_index, stations = build_distance_matrix(routes)

        # Measure the execution time of the Floyd-Warshall algorithm
        start_time = time.time()
        shortest_paths, next_node = floyd(duration_matrix, line_matrix)
        end_time = time.time()

        # Reconstruct the path
        path, lines = reconstruct_path2(start, end, next_node, line_matrix, station_index, stations)
        total_duration = shortest_paths[station_index[start]][station_index[end]]

        if not path:
            return jsonify({'route': 'null'}), 400
        else:
            response = {
                'route': path,
                'duration': total_duration,
                'execution_time': end_time - start_time
            }
            return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bellmanford/')
def api_bellmanford():
    try:
        req = request.args
        start = req.get('start').strip().lower()
        end = req.get('end').strip().lower()

        # Check if the start and end stations exist in the graph
        if start not in stations:
            return jsonify({'error': f'Start station {start} not found in the graph.'}), 400
        if end not in stations:
            return jsonify({'error': f'End station {end} not found in the graph.'}), 400

        path, total_distance, total_duration = bellman_ford(stations, start, end)
        
        if not path:
            return jsonify({'route': 'null'}), 400
        else:
            return jsonify({'route': path, 'duration': total_duration}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search/')
def api_search():
    try:
        query = request.args.get('query', '').strip().lower()
        results = sequential_search(stations, query)
        return jsonify({'results': results}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/binarysearch/')
def api_binary_search():
    try:
        query = request.args.get('query', '').strip().lower()
        if not query:
            raise ValueError("Query is empty")
        results = binary_search(stations, query)
        return jsonify({'results': results}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/liveCrowdDensity', methods=['GET'])
def get_train_data():
    try:
        train_line = request.args.get('TrainLine', 'NSL')  # Default to 'NorthSouth' if not provided
        headers = {
            'AccountKey': 'YOUR API KEY',
            'accept': 'application/json'
        }
        response = requests.get(f'http://datamall2.mytransport.sg/ltaodataservice/PCDRealTime?TrainLine={train_line}', headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)