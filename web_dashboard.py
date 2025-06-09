from flask import Flask, render_template_string, request, redirect, session, url_for, send_file, jsonify
import logging
import io
import matplotlib.pyplot as plt
import networkx as nx
from datetime import datetime
from roadmesh.monitoring.battery import BatteryChargeMonitoring
from roadmesh.monitoring.lighting import LightingController
from roadmesh.networking.mesh_manager import MeshNetworkManager
from roadmesh.networking.user_service import UserServiceManager
from roadmesh.monitoring.health_monitor import HealthMonitor
from roadmesh.monitoring.power_management import PowerManagement
from roadmesh.persistence import load_battery_history, load_event_log, load_mesh_status_history
import secrets

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change for production
logger = logging.getLogger(__name__)

# Initialize subsystems (in production, pass real objects)
battery = BatteryChargeMonitoring(5.0, 0.2)
lighting = LightingController(battery)
mesh = MeshNetworkManager()
user_service = UserServiceManager()
power_mgmt = PowerManagement(battery, lighting, mesh)
health_monitor = HealthMonitor(battery, lighting, mesh, user_service)

RECENT_ALERTS = []

# Helper for health status color
HEALTH_COLOR = {True: 'green', False: 'red'}
MODE_COLOR = {'on': 'green', 'dim': 'orange', 'off': 'gray', 'emergency': 'red',
              'normal': 'green', 'reduced': 'orange', 'critical': 'red'}
LIGHT_COLOR = {'ON': 'yellow', 'DIM': 'orange', 'OFF': 'gray', 'EMERGENCY': 'red'}

API_KEY = 'changemeapikey'  # Set a secure key for production

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    pct = battery.calculate_percentage()
    lighting_state = lighting.state
    mesh_topology = mesh.get_topology()
    sessions = user_service.sessions
    health = {
        'battery': battery.health_check(),
        'lighting': lighting.health_check(),
        'mesh': mesh.health_check(),
        'user': user_service.health_check()
    }
    lighting_mode = power_mgmt.lighting_mode
    mesh_mode = power_mgmt.mode
    mesh_statuses = mesh.get_node_statuses()
    light_statuses = lighting.get_light_statuses()
    return render_template_string('''
    <h1>RoadMesh Dashboard</h1>
    <a href="{{ url_for('analytics') }}">Analytics & Event Log</a><br>
    <p>Battery: {{ pct }}%</p>
    <img src="{{ url_for('battery_plot') }}" alt="Battery Plot" height="200"><br>
    <p>Lighting: {{ lighting_state }} (<span style="color:{{ mode_color[lighting_mode] }}">{{ lighting_mode }}</span>)</p>
    <img src="{{ url_for('lighting_map') }}" alt="Lighting Map" height="40"><br>
    <form method="post" action="/lighting">
        <button name="action" value="ON">ON</button>
        <button name="action" value="OFF">OFF</button>
        <button name="action" value="DIM">DIM</button>
    </form>
    <p>Mesh Topology: {{ mesh_topology }}</p>
    <p>Mesh Mode: <span style="color:{{ mode_color[mesh_mode] }}">{{ mesh_mode }}</span></p>
    <img src="{{ url_for('mesh_graph') }}" alt="Mesh Graph" height="200"><br>
    <h3>Mesh Node Status</h3>
    <table border="1"><tr><th>Node</th><th>Status</th><th>Power Mode</th><th>Bandwidth</th></tr>
    {% for node, (status, power_mode, bandwidth) in mesh_statuses.items() %}
      <tr><td>{{ node }}</td><td>{{ status }}</td><td>{{ power_mode }}</td><td>{{ bandwidth }}</td></tr>
    {% endfor %}
    </table>
    <h3>Lighting Status</h3>
    <table border="1"><tr><th>Light</th><th>Status</th></tr>
    {% for idx, state in light_statuses %}
      <tr><td>{{ idx }}</td><td>{{ state }}</td></tr>
    {% endfor %}
    </table>
    <p>Active Sessions: {{ sessions }}</p>
    <h2>Health Status</h2>
    <ul>
      <li>Battery: <span style="color:{{ health_color[health['battery']] }}">{{ health['battery'] }}</span></li>
      <li>Lighting: <span style="color:{{ health_color[health['lighting']] }}">{{ health['lighting'] }}</span></li>
      <li>Mesh: <span style="color:{{ health_color[health['mesh']] }}">{{ health['mesh'] }}</span></li>
      <li>User: <span style="color:{{ health_color[health['user']] }}">{{ health['user'] }}</span></li>
    </ul>
    <h2>Recent Alerts</h2>
    <ul>
    {% for alert in recent_alerts %}
      <li>{{ alert }}</li>
    {% endfor %}
    </ul>
    <a href="{{ url_for('logout') }}">Logout</a>
    {% if session['user'] == 'admin' %}
    <h2>Register New User</h2>
    <form method="post" action="/register">
        Username: <input name="username"><br>
        Password: <input name="password" type="password"><br>
        <input type="submit" value="Register">
    </form>
    {% endif %}
    ''', pct=pct, lighting_state=lighting_state, lighting_mode=lighting_mode, mesh_mode=mesh_mode,
         mesh_topology=mesh.get_topology(), mesh_statuses=mesh_statuses, light_statuses=light_statuses,
         mesh_graph=mesh_topology_graph(), sessions=sessions,
         health=health, health_color=HEALTH_COLOR, mode_color=MODE_COLOR, recent_alerts=RECENT_ALERTS)

@app.route('/lighting', methods=['POST'])
def lighting_control():
    if 'user' not in session:
        return redirect(url_for('login'))
    action = request.form['action']
    if action == 'ON':
        lighting.turn_on()
        power_mgmt.lighting_mode = 'on'
    elif action == 'OFF':
        lighting.turn_off()
        power_mgmt.lighting_mode = 'off'
    elif action == 'DIM':
        lighting.dim()
        power_mgmt.lighting_mode = 'dim'
    RECENT_ALERTS.append(f"Lighting set to {action} by {session['user']}")
    return redirect(url_for('index'))

@app.route('/battery_plot')
def battery_plot():
    # Plot battery voltage history
    plt.figure(figsize=(4,2))
    times = [d['timestamp'] for d in battery.voltage_data]
    volts = [d['voltage'] for d in battery.voltage_data]
    plt.plot(times, volts, label='Voltage')
    plt.xlabel('Time')
    plt.ylabel('Voltage (V)')
    plt.legend()
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@app.route('/mesh_graph')
def mesh_graph():
    # Draw mesh topology as a graph
    G = nx.Graph()
    topo = mesh.get_topology()
    for node, neighbors in topo.items():
        for n in neighbors:
            G.add_edge(node, n)
    node_statuses = mesh.get_node_statuses()
    color_map = []
    for node in G.nodes():
        status, power_mode, _ = node_statuses.get(node, ('DOWN', 'off', 0))
        if status == 'UP' and power_mode == 'normal':
            color_map.append('green')
        elif status == 'UP' and power_mode == 'reduced':
            color_map.append('orange')
        elif status == 'UP' and power_mode == 'critical':
            color_map.append('red')
        else:
            color_map.append('gray')
    plt.figure(figsize=(4,2))
    nx.draw(G, with_labels=True, node_color=color_map, node_size=500)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@app.route('/lighting_map')
def lighting_map():
    # Draw lighting as a row of colored circles
    statuses = lighting.get_light_statuses()
    plt.figure(figsize=(6,1))
    for i, (_, state) in enumerate(statuses):
        plt.scatter(i, 0, s=800, c=LIGHT_COLOR.get(state, 'gray'), edgecolors='black')
    plt.axis('off')
    plt.xlim(-1, len(statuses))
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
    plt.close()
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

def mesh_topology_graph():
    # Simple text graph
    topo = mesh.get_topology()
    lines = []
    for node, neighbors in topo.items():
        lines.append(f"{node}: {', '.join(neighbors)}")
    return '\n'.join(lines)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if user_service.authenticate(username, password):
            session['user'] = username
            user_service.create_session(username)
            return redirect(url_for('index'))
        else:
            return 'Login failed', 401
    return render_template_string('''
    <h1>Login</h1>
    <form method="post">
        Username: <input name="username"><br>
        Password: <input name="password" type="password"><br>
        <input type="submit" value="Login">
    </form>
    ''')

@app.route('/logout')
def logout():
    user = session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['POST'])
def register():
    if 'user' not in session or session['user'] != 'admin':
        return 'Unauthorized', 403
    username = request.form['username']
    password = request.form['password']
    if user_service.register_user(username, password):
        RECENT_ALERTS.append(f"User {username} registered by admin.")
        return redirect(url_for('index'))
    else:
        return 'Registration failed', 400

@app.route('/analytics')
def analytics():
    # Battery trend
    battery_history = load_battery_history()
    times = [row['timestamp'] for row in battery_history]
    volts = [float(row['voltage']) for row in battery_history if row['voltage']]
    charge = [float(row['charge_pct']) for row in battery_history if row['charge_pct']]
    # Mesh uptime analytics
    mesh_status_history = load_mesh_status_history()
    total_steps = len(mesh_status_history)
    all_up_steps = 0
    node_up_counts = {}
    for record in mesh_status_history:
        statuses = record['node_statuses']
        up_nodes = [n for n, (status, _, _) in statuses.items() if status == 'UP']
        if len(up_nodes) == len(statuses):
            all_up_steps += 1
        for n in statuses:
            if n not in node_up_counts:
                node_up_counts[n] = 0
            if statuses[n][0] == 'UP':
                node_up_counts[n] += 1
    mesh_uptime = f"{(all_up_steps/total_steps*100):.1f}%" if total_steps else 'N/A'
    mesh_reliability = f"{(sum(node_up_counts.values())/(total_steps*len(node_up_counts))*100):.1f}%" if total_steps and node_up_counts else 'N/A'
    # Lighting ON hours (count ON in history)
    lighting_on_hours = sum(1 for v in charge if v > 50)
    # Forecast battery depletion/recharge (simple linear extrapolation)
    forecast = 'N/A'
    if len(charge) > 2:
        delta = charge[-1] - charge[0]
        hours = len(charge)
        if delta < 0:
            # Depleting
            rate = abs(delta) / hours
            if rate > 0:
                forecast = f"Deplete in {(charge[-1]/rate):.1f} hours"
        elif delta > 0:
            # Charging
            rate = delta / hours
            if rate > 0:
                forecast = f"Full in {((100-charge[-1])/rate):.1f} hours"
    # Event log
    event_log = load_event_log()
    return render_template_string('''
    <h1>Analytics & Event Log</h1>
    <a href="{{ url_for('index') }}">Back to Dashboard</a><br>
    <h2>Battery Trend</h2>
    <img src="{{ url_for('battery_trend_plot') }}" alt="Battery Trend" height="200"><br>
    <h2>Mesh Uptime</h2>
    <p>{{ mesh_uptime }}</p>
    <h2>Mesh Reliability</h2>
    <p>{{ mesh_reliability }}</p>
    <h2>Lighting ON Hours</h2>
    <p>{{ lighting_on_hours }}</p>
    <h2>Battery Forecast</h2>
    <p>{{ forecast }}</p>
    <h2>Event Log</h2>
    <table border="1"><tr><th>Timestamp</th><th>Event</th></tr>
    {% for row in event_log %}
      <tr><td>{{ row['timestamp'] }}</td><td>{{ row['event'] }}</td></tr>
    {% endfor %}
    </table>
    ''', mesh_uptime=mesh_uptime, mesh_reliability=mesh_reliability, lighting_on_hours=lighting_on_hours, forecast=forecast, event_log=event_log)

@app.route('/battery_trend_plot')
def battery_trend_plot():
    battery_history = load_battery_history()
    times = [datetime.fromisoformat(row['timestamp']) for row in battery_history if row['timestamp']]
    charge = [float(row['charge_pct']) for row in battery_history if row['charge_pct']]
    plt.figure(figsize=(4,2))
    plt.plot(times, charge, label='Charge %')
    plt.xlabel('Time')
    plt.ylabel('Charge (%)')
    plt.legend()
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@app.route('/api/events', methods=['GET'])
def api_events():
    auth = require_api_key()
    if auth: return auth
    return jsonify(load_event_log())

@app.route('/rotate_api_key', methods=['POST'])
def rotate_api_key():
    if 'user' not in session or session['user'] != 'admin':
        return 'Unauthorized', 403
    global API_KEY
    API_KEY = secrets.token_hex(16)
    return f'API key rotated. New key: {API_KEY}'

if __name__ == '__main__':
    app.run(debug=True, ssl_context='adhoc') 