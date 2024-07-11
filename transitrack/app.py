from flask import Flask, request, render_template, jsonify
from graph import load_graph, dfs, build_distance_map, a_star, dijkstras, sequential_search, bfs, bellman_ford, binary_search
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

stations = load_graph('static/route.json')
distance_map = build_distance_map(stations)  # Build distance map once
    
@app.route('/')
def index():
    return render_template('index.html')

# xen is gay
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

@app.route('/api/floyd/')
def api_floyd():
    try:
        req = request.args
        start = req.get('start').strip().lower()
        end = req.get('end').strip().lower()

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