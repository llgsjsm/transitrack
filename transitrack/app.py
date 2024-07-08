from flask import Flask, request, render_template, jsonify
from graph import load_graph, dfs, build_distance_map, heuristic, a_star, reconstruct_path, dijkstras, sequential_search, load_graph2, bfs

app = Flask(__name__)

stations = load_graph('static/route.json')
djik1, djik2 = load_graph2('static/route.json')
distance_map = build_distance_map(stations)  # Build distance map once

@app.route('/')
def index():
    return render_template('index.html')

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

        shortest_path, path, lines = dijkstras(djik1, start, end, djik2)
        if not path:
            return jsonify({'route': 'null'}), 400
        else:
            return jsonify({'route': path, 'duration': shortest_path}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bfs/')
def api_bfs():
    try:
        req = request.args
        start = req.get('start').strip().lower()
        end = req.get('end').strip().lower()

        bfs1, bfs2 = load_graph2('static/route.json')
        # Check if the start and end stations exist in the graph
        if start not in stations:
            return jsonify({'error': f'Start station {start} not found in the graph.'}), 400
        if end not in stations:
            return jsonify({'error': f'End station {end} not found in the graph.'}), 400

        path, lines, total_distance, total_duration = bfs(bfs1, start, end)
        
        if not path:
            return jsonify({'route': 'null'}), 400
        else:
            return jsonify({'route': path, 'duration': total_duration}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#aaron
@app.route('/api/search/')
def api_search():
    try:
        query = request.args.get('query', '').strip().lower()
        results = sequential_search(stations, query)
        return jsonify({'results': results}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
