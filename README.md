# AutoRescue - Smart Accident Detection System

AutoRescue is a web-based smart accident detection system that continuously monitors driver's smartphone motion data (gyroscope and accelerometer) to detect potential accidents and automatically send SOS alerts to an Admin Dashboard.

## Features

- **Real-time Motion Monitoring**: Uses device motion sensors to detect accidents
- **Automatic SOS Alerts**: Sends alerts automatically when accident thresholds are exceeded
- **Manual SOS**: Drivers can manually trigger emergency alerts
- **Admin Dashboard**: Real-time alert management and verification
- **GPS Location Tracking**: Captures precise location data for emergency response
- **Multi-user Support**: Separate interfaces for drivers and administrators

## Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (DeviceMotion API, Fetch API)
- **Backend**: Python Flask
- **Database**: SQLAlchemy ORM with SQLite
- **UI Framework**: Bootstrap 5
- **Icons**: Font Awesome

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd autorescue
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - Use the demo credentials or register a new account

## Demo Credentials

- **Admin Account**: 
  - Username: `admin`
  - Password: `admin123`

- **Driver Account**: Register a new account through the registration form

## Usage

### For Drivers

1. **Login** to the driver dashboard
2. **Grant permissions** for motion sensors and location access
3. **Start monitoring** to begin accident detection
4. **Keep the browser tab open** for continuous monitoring
5. **Manual SOS** button available for emergency situations

### For Administrators

1. **Login** with admin credentials
2. **View real-time alerts** in the admin dashboard
3. **Verify alerts** for authenticity
4. **Dispatch alerts** to emergency responders
5. **Mark alerts as resolved** when response is complete

## System Flow

1. **Driver Login** → Activates motion monitoring
2. **Continuous Monitoring** → Analyzes sensor data in real-time
3. **Accident Detection** → Triggers when acceleration > 25 m/s²
4. **Automatic SOS** → Sends alert with GPS coordinates
5. **Admin Notification** → Real-time alert appears in dashboard
6. **Alert Verification** → Admin verifies and dispatches to responders
7. **Response Tracking** → Monitor and resolve alerts

## API Endpoints

- `POST /api/alerts` - Create a new alert
- `GET /api/alerts` - Retrieve alerts list
- `PATCH /api/alerts/<id>/verify` - Verify an alert
- `PATCH /api/alerts/<id>/dispatch` - Dispatch alert to responders
- `PATCH /api/alerts/<id>/resolve` - Mark alert as resolved
- `GET /api/health` - System health check

## Configuration

### Accident Detection Threshold
The system uses a configurable threshold for accident detection:
- **Default**: 25 m/s² acceleration magnitude
- **Location**: Driver dashboard JavaScript (can be modified)

### Database
- **Default**: SQLite database (`autorescue.db`)
- **Location**: Project root directory
- **Tables**: `users`, `alerts`

## Security Considerations

- **HTTPS Required**: For production deployment, ensure HTTPS is enabled
- **Sensor Permissions**: Browser requires user permission for motion sensors
- **Location Privacy**: GPS data is only used for emergency response
- **Session Management**: User sessions are managed securely

## Browser Compatibility

- **Chrome**: Full support for DeviceMotion API
- **Firefox**: Full support for DeviceMotion API
- **Safari**: Full support for DeviceMotion API
- **Edge**: Full support for DeviceMotion API

## Mobile Testing

For best results, test the accident detection on actual mobile devices:
1. Open the application in mobile browser
2. Grant motion sensor permissions
3. Start monitoring
4. Simulate motion (shake device) to test detection

## Troubleshooting

### Motion Sensors Not Working
- Ensure browser has permission for motion sensors
- Test on actual mobile device (not desktop)
- Check browser console for permission errors

### Location Not Available
- Grant location permission when prompted
- Ensure device GPS is enabled
- Test in outdoor environment for better GPS accuracy

### Alerts Not Sending
- Check internet connection
- Verify backend server is running
- Check browser console for API errors

## Future Enhancements

- Real-time updates using WebSockets
- Push notifications for mobile devices
- AI/ML impact severity prediction
- Google Maps integration for responder routing
- Multi-tenant support for different organizations
- Advanced analytics and reporting

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support
## Deploying to Vercel

This repo is pre-configured for Vercel serverless deployment.

### Steps
1. Push your project to GitHub.
2. In Vercel, import the repo.
3. Framework Preset: Other.
4. Python Runtime: Uses `python3.11` via `vercel.json`.
5. Install command: `pip install -r requirements.txt`.
6. Vercel will use `api/index.py` as the serverless entry to run the Flask app.

### Notes
- Vercel is HTTPS by default, so mobile geolocation and motion sensor permissions will prompt and work.
- SQLite is not ideal on serverless; set `DATABASE_URL` (e.g., Neon/Postgres, PlanetScale/MySQL) as an Environment Variable in Vercel. The app will automatically use it via SQLAlchemy if provided.
- If you split static hosting and API, keep routes to `api/index.py` or create a separate frontend.

### Environment Variables
- `FLASK_ENV=production`
- `DATABASE_URL=<your_database_connection_string>`


For support and questions, please contact the development team or create an issue in the repository.
