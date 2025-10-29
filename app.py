from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash
from config import config

app = Flask(__name__)
try:
    CORS(app, supports_credentials=True)
except Exception:
    pass
config_name = os.environ.get('FLASK_ENV', 'default')
app.config.from_object(config[config_name])

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_ambulance_driver = db.Column(db.Boolean, default=False)
    driver_id = db.Column(db.String(50), unique=True, nullable=True)  # Ambulance driver ID
    current_latitude = db.Column(db.Float, nullable=True)
    current_longitude = db.Column(db.Float, nullable=True)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(db.String(50), nullable=False)  # 'Accident' or 'Manual SOS'
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    resolved = db.Column(db.Boolean, default=False)
    details = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    impact_magnitude = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, verified, dispatched, accepted, resolved
    assigned_ambulance_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    accepted_at = db.Column(db.DateTime, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)

# API Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        session['username'] = user.username
        session['is_admin'] = user.is_admin
        session['is_ambulance_driver'] = user.is_ambulance_driver
        return jsonify({
            'success': True, 
            'is_admin': user.is_admin,
            'is_ambulance_driver': user.is_ambulance_driver
        })
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': 'Username already exists'})
    
    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': 'Email already exists'})
    
    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password)
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'User created successfully'})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    if session.get('is_admin'):
        return render_template('admin_dashboard.html')
    elif session.get('is_ambulance_driver'):
        return render_template('ambulance_dashboard.html')
    else:
        return render_template('driver_dashboard.html')

# API Endpoints
@app.route('/api/alerts', methods=['POST'])
def create_alert():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    
    alert = Alert(
        alert_type=data.get('alert_type', 'Accident'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        details=data.get('details', ''),
        user_id=session['user_id'],
        impact_magnitude=data.get('impact_magnitude')
    )
    
    db.session.add(alert)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'alert_id': alert.id,
        'message': 'Alert created successfully'
    })

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if session.get('is_admin'):
        alerts = Alert.query.order_by(Alert.timestamp.desc()).all()
    else:
        alerts = Alert.query.filter_by(user_id=session['user_id']).order_by(Alert.timestamp.desc()).all()
    
    alerts_data = []
    for alert in alerts:
        alerts_data.append({
            'id': alert.id,
            'alert_type': alert.alert_type,
            'latitude': alert.latitude,
            'longitude': alert.longitude,
            'timestamp': alert.timestamp.isoformat(),
            'resolved': alert.resolved,
            'details': alert.details,
            'impact_magnitude': alert.impact_magnitude,
            'status': alert.status,
            'assigned_ambulance_id': alert.assigned_ambulance_id,
            'accepted_at': alert.accepted_at.isoformat() if alert.accepted_at else None,
            'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None
        })
    
    return jsonify(alerts_data)

@app.route('/api/alerts/<int:alert_id>/resolve', methods=['PATCH'])
def resolve_alert(alert_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    alert = Alert.query.get_or_404(alert_id)
    alert.resolved = True
    alert.status = 'resolved'
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Alert resolved'})

@app.route('/api/alerts/<int:alert_id>/verify', methods=['PATCH'])
def verify_alert(alert_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    alert = Alert.query.get_or_404(alert_id)
    alert.status = 'verified'
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Alert verified'})

@app.route('/api/alerts/<int:alert_id>/dispatch', methods=['PATCH'])
def dispatch_alert(alert_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    alert = Alert.query.get_or_404(alert_id)
    alert.status = 'dispatched'
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Alert dispatched to responders'})

@app.route('/api/ambulance/update-location', methods=['POST'])
def update_ambulance_location():
    if 'user_id' not in session or not session.get('is_ambulance_driver'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    user = User.query.get(session['user_id'])
    
    if user:
        user.current_latitude = data.get('latitude')
        user.current_longitude = data.get('longitude')
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/ambulance/accept-alert/<int:alert_id>', methods=['POST'])
def accept_alert(alert_id):
    if 'user_id' not in session or not session.get('is_ambulance_driver'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    alert = Alert.query.get_or_404(alert_id)
    
    # Check if alert is already accepted
    if alert.status == 'accepted':
        return jsonify({'error': 'Alert already accepted by another driver'}), 400
    
    # Update alert status
    alert.status = 'accepted'
    alert.assigned_ambulance_id = session['user_id']
    alert.accepted_at = datetime.utcnow()
    
    # Mark driver as unavailable
    user = User.query.get(session['user_id'])
    if user:
        user.is_available = False
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Alert accepted successfully'})

@app.route('/api/ambulance/resolve-alert/<int:alert_id>', methods=['POST'])
def resolve_alert_by_ambulance(alert_id):
    if 'user_id' not in session or not session.get('is_ambulance_driver'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    alert = Alert.query.get_or_404(alert_id)
    
    # Check if this driver is assigned to this alert
    if alert.assigned_ambulance_id != session['user_id']:
        return jsonify({'error': 'Not authorized to resolve this alert'}), 403
    
    # Update alert status
    alert.status = 'resolved'
    alert.resolved = True
    alert.resolved_at = datetime.utcnow()
    
    # Mark driver as available again
    user = User.query.get(session['user_id'])
    if user:
        user.is_available = True
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Alert resolved successfully'})

@app.route('/api/ambulance/alerts')
def get_ambulance_alerts():
    if 'user_id' not in session or not session.get('is_ambulance_driver'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get dispatched alerts (not yet accepted)
    dispatched_alerts = Alert.query.filter_by(status='dispatched').all()
    
    alerts_data = []
    for alert in dispatched_alerts:
        alerts_data.append({
            'id': alert.id,
            'alert_type': alert.alert_type,
            'latitude': alert.latitude,
            'longitude': alert.longitude,
            'timestamp': alert.timestamp.isoformat(),
            'details': alert.details,
            'impact_magnitude': alert.impact_magnitude,
            'status': alert.status
        })
    
    return jsonify(alerts_data)

@app.route('/api/ambulance/my-alerts')
def get_my_ambulance_alerts():
    if 'user_id' not in session or not session.get('is_ambulance_driver'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get alerts assigned to this driver
    my_alerts = Alert.query.filter_by(assigned_ambulance_id=session['user_id']).order_by(Alert.timestamp.desc()).all()
    
    alerts_data = []
    for alert in my_alerts:
        alerts_data.append({
            'id': alert.id,
            'alert_type': alert.alert_type,
            'latitude': alert.latitude,
            'longitude': alert.longitude,
            'timestamp': alert.timestamp.isoformat(),
            'accepted_at': alert.accepted_at.isoformat() if alert.accepted_at else None,
            'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None,
            'details': alert.details,
            'impact_magnitude': alert.impact_magnitude,
            'status': alert.status
        })
    
    return jsonify(alerts_data)

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create admin user if it doesn't exist
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@autorescue.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: username=admin, password=admin123")
        
        # Create sample ambulance driver if it doesn't exist
        ambulance = User.query.filter_by(username='ambulance1').first()
        if not ambulance:
            ambulance = User(
                username='ambulance1',
                email='ambulance1@autorescue.com',
                password_hash=generate_password_hash('ambulance123'),
                is_ambulance_driver=True,
                driver_id='AMB001',
                is_available=True
            )
            db.session.add(ambulance)
            db.session.commit()
            print("Ambulance driver created: username=ambulance1, password=ambulance123")
    
    # Optional HTTPS support for mobile geolocation (required by browsers over network)
    # Configure via env:
    #   AUTORESCUE_SSL=adhoc            -> use generated self-signed cert
    #   AUTORESCUE_SSL=cert             -> use cert.pem/key.pem in project root (or set CERT_PATH/KEY_PATH)
    ssl_context = None
    ssl_mode = os.environ.get('AUTORESCUE_SSL')
    if ssl_mode:
        try:
            if ssl_mode.lower() == 'adhoc':
                # Werkzeug can generate an adhoc self-signed certificate
                ssl_context = 'adhoc'
                print("Starting server with ADHOC HTTPS (self-signed)")
            elif ssl_mode.lower() == 'cert':
                cert_path = os.environ.get('CERT_PATH', 'cert.pem')
                key_path = os.environ.get('KEY_PATH', 'key.pem')
                if os.path.exists(cert_path) and os.path.exists(key_path):
                    ssl_context = (cert_path, key_path)
                    print(f"Starting server with HTTPS using cert: {cert_path}, key: {key_path}")
                else:
                    print("CERT/KEY files not found, falling back to HTTP. Set CERT_PATH/KEY_PATH or place cert.pem/key.pem in root.")
            else:
                print("Unknown AUTORESCUE_SSL value. Use 'adhoc' or 'cert'. Starting HTTP.")
        except Exception as e:
            print(f"Failed to configure SSL: {e}. Starting HTTP.")

    app.run(debug=True, host='0.0.0.0', port=5000, ssl_context=ssl_context)
