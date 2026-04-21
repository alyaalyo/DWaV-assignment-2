from flask import Flask, request, jsonify, Response, send_from_directory
import json
import os
import queue
import threading

app = Flask(__name__, static_folder='static')

_clients_lock = threading.Lock()
_clients: list[queue.Queue] = []
_history: list[str] = []


@app.route('/health')
def health():
    return jsonify({'status': 'ok'})


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/receive')
def receive():
    try:
        package = {
            'ip': request.args.get('ip'),
            'lat': float(request.args.get('lat')),
            'lon': float(request.args.get('lon')),
            'timestamp': float(request.args.get('timestamp')),
            'suspicious': int(request.args.get('suspicious', 0))
        }
    except (TypeError, ValueError) as e:
        return jsonify({'error': str(e)}), 400

    data = json.dumps(package)
    with _clients_lock:
        _history.append(data)
        dead = []
        for q in _clients:
            try:
                q.put_nowait(data)
            except queue.Full:
                dead.append(q)
        for q in dead:
            _clients.remove(q)

    return jsonify({'status': 'ok'})


def _generate_events(q: queue.Queue):
    try:
        while True:
            try:
                data = q.get(timeout=20)
                yield f'data: {data}\n\n'
            except queue.Empty:
                yield ': heartbeat\n\n'
    except GeneratorExit:
        pass
    finally:
        with _clients_lock:
            if q in _clients:
                _clients.remove(q)


@app.route('/stream')
def stream():
    q: queue.Queue = queue.Queue(maxsize=5000)
    with _clients_lock:
        for item in _history:
            q.put_nowait(item)
        _clients.append(q)
    return Response(
        _generate_events(q),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        }
    )


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)
