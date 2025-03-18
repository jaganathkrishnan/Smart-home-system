from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from virtual_arduino import VirtualArduino

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
arduino = VirtualArduino()

@app.route('/')
def index():
    return render_template('index.html', led_state=arduino.get_led_state())

@app.route('/control', methods=['POST'])
def control():
    action = request.form['action']
    if action == 'on':
        arduino.turn_on_led()
        led_state = True
    elif action == 'off':
        arduino.turn_off_led()
        led_state = False

    socketio.emit('led_state', {'state': led_state})  # Notify frontend
    return jsonify({'led_state': led_state})

# Listen for WebSocket events from gesture_recognition.py
@socketio.on('led_state')
def handle_led_state(data):
    state = data['state']
    if state:
        arduino.turn_on_led()
    else:
        arduino.turn_off_led()

    print(f"LED state changed: {'ON' if state else 'OFF'}")
    socketio.emit('led_state', {'state': state})  # Notify frontend

if __name__ == '__main__':
    socketio.run(app, debug=True)
