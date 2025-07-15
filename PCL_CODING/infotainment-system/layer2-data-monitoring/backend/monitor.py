from flask import Flask, jsonify, request
from flask_cors import CORS
import psutil
import time
import threading
from datetime import datetime, timedelta
import json
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data storage for monitoring
monitoring_data = {
    "system_metrics": {
        "cpu_usage": 0,
        "memory_usage": 0,
        "disk_usage": 0,
        "network_io": {"bytes_sent": 0, "bytes_recv": 0}
    },
    "vehicle_metrics": {
        "speed": 0,
        "rpm": 0,
        "fuel_level": 0,
        "temperature": 0,
        "mileage": 0
    },
    "alerts": [],
    "logs": [],
    "timestamp": datetime.now().isoformat()
}

# Monitoring configuration
monitoring_config = {
    "monitoring_enabled": True,
    "alert_thresholds": {
        "cpu_usage": 80,
        "memory_usage": 85,
        "fuel_level": 20,
        "temperature": 85,
        "speed": 90
    },
    "log_retention_hours": 24
}

class DataMonitor:
    def __init__(self):
        self.running = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Start the monitoring thread"""
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            logger.info("Data monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("Data monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                self._collect_system_metrics()
                self._collect_vehicle_metrics()
                self._check_alerts()
                self._cleanup_old_logs()
                time.sleep(5)  # Monitor every 5 seconds
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
    
    def _collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            monitoring_data["system_metrics"]["cpu_usage"] = psutil.cpu_percent()
            monitoring_data["system_metrics"]["memory_usage"] = psutil.virtual_memory().percent
            monitoring_data["system_metrics"]["disk_usage"] = psutil.disk_usage('/').percent
            
            net_io = psutil.net_io_counters()
            monitoring_data["system_metrics"]["network_io"] = {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv
            }
            
            monitoring_data["timestamp"] = datetime.now().isoformat()
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    def _collect_vehicle_metrics(self):
        """Simulate vehicle metrics collection"""
        import random
        
        # Simulate vehicle data (in a real system, this would come from vehicle sensors)
        monitoring_data["vehicle_metrics"] = {
            "speed": random.randint(45, 95),
            "rpm": random.randint(1800, 3200),
            "fuel_level": max(0, monitoring_data["vehicle_metrics"]["fuel_level"] - random.uniform(0, 0.1)),
            "temperature": random.randint(65, 90),
            "mileage": monitoring_data["vehicle_metrics"]["mileage"] + random.uniform(0, 0.01)
        }
    
    def _check_alerts(self):
        """Check for alert conditions"""
        alerts = []
        thresholds = monitoring_config["alert_thresholds"]
        
        # System alerts
        if monitoring_data["system_metrics"]["cpu_usage"] > thresholds["cpu_usage"]:
            alerts.append({
                "type": "system",
                "severity": "warning",
                "message": f"High CPU usage: {monitoring_data['system_metrics']['cpu_usage']:.1f}%",
                "timestamp": datetime.now().isoformat()
            })
        
        if monitoring_data["system_metrics"]["memory_usage"] > thresholds["memory_usage"]:
            alerts.append({
                "type": "system",
                "severity": "warning",
                "message": f"High memory usage: {monitoring_data['system_metrics']['memory_usage']:.1f}%",
                "timestamp": datetime.now().isoformat()
            })
        
        # Vehicle alerts
        if monitoring_data["vehicle_metrics"]["fuel_level"] < thresholds["fuel_level"]:
            alerts.append({
                "type": "vehicle",
                "severity": "critical",
                "message": f"Low fuel level: {monitoring_data['vehicle_metrics']['fuel_level']:.1f}%",
                "timestamp": datetime.now().isoformat()
            })
        
        if monitoring_data["vehicle_metrics"]["temperature"] > thresholds["temperature"]:
            alerts.append({
                "type": "vehicle",
                "severity": "warning",
                "message": f"High engine temperature: {monitoring_data['vehicle_metrics']['temperature']}°F",
                "timestamp": datetime.now().isoformat()
            })
        
        if monitoring_data["vehicle_metrics"]["speed"] > thresholds["speed"]:
            alerts.append({
                "type": "vehicle",
                "severity": "warning",
                "message": f"Speed limit exceeded: {monitoring_data['vehicle_metrics']['speed']} mph",
                "timestamp": datetime.now().isoformat()
            })
        
        # Add new alerts to the list
        for alert in alerts:
            monitoring_data["alerts"].append(alert)
            self._log_event(f"ALERT: {alert['message']}", alert['severity'].upper())
        
        # Keep only recent alerts (last 100)
        monitoring_data["alerts"] = monitoring_data["alerts"][-100:]
    
    def _log_event(self, message, level="INFO"):
        """Log an event"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message
        }
        monitoring_data["logs"].append(log_entry)
        logger.info(f"{level}: {message}")
    
    def _cleanup_old_logs(self):
        """Remove old log entries"""
        cutoff_time = datetime.now() - timedelta(hours=monitoring_config["log_retention_hours"])
        monitoring_data["logs"] = [
            log for log in monitoring_data["logs"]
            if datetime.fromisoformat(log["timestamp"]) > cutoff_time
        ]

# Initialize monitor
monitor = DataMonitor()

@app.route('/')
def home():
    return jsonify({
        "message": "Infotainment System - Layer 2 Data Monitoring",
        "status": "running",
        "monitoring_enabled": monitoring_config["monitoring_enabled"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/monitor')
def get_monitoring_data():
    """Get all monitoring data"""
    return jsonify(monitoring_data)

@app.route('/api/system-metrics')
def get_system_metrics():
    """Get system performance metrics"""
    return jsonify({
        "system_metrics": monitoring_data["system_metrics"],
        "timestamp": monitoring_data["timestamp"]
    })

@app.route('/api/vehicle-metrics')
def get_vehicle_metrics():
    """Get vehicle performance metrics"""
    return jsonify({
        "vehicle_metrics": monitoring_data["vehicle_metrics"],
        "timestamp": monitoring_data["timestamp"]
    })

@app.route('/api/alerts')
def get_alerts():
    """Get recent alerts"""
    return jsonify({
        "alerts": monitoring_data["alerts"][-20:],  # Last 20 alerts
        "total_alerts": len(monitoring_data["alerts"])
    })

@app.route('/api/logs')
def get_logs():
    """Get recent logs"""
    return jsonify({
        "logs": monitoring_data["logs"][-50:],  # Last 50 logs
        "total_logs": len(monitoring_data["logs"])
    })

@app.route('/api/start-monitoring', methods=['POST'])
def start_monitoring():
    """Start data monitoring"""
    monitor.start_monitoring()
    monitor._log_event("Data monitoring started", "INFO")
    return jsonify({
        "message": "Data monitoring started",
        "status": "success",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/stop-monitoring', methods=['POST'])
def stop_monitoring():
    """Stop data monitoring"""
    monitor.stop_monitoring()
    monitor._log_event("Data monitoring stopped", "INFO")
    return jsonify({
        "message": "Data monitoring stopped",
        "status": "success",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/config', methods=['GET', 'POST'])
def monitoring_configuration():
    """Get or update monitoring configuration"""
    if request.method == 'GET':
        return jsonify(monitoring_config)
    else:
        data = request.get_json()
        monitoring_config.update(data)
        monitor._log_event("Monitoring configuration updated", "INFO")
        return jsonify({
            "message": "Configuration updated",
            "config": monitoring_config,
            "timestamp": datetime.now().isoformat()
        })

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "layer": "Layer 2 - Data Monitoring",
        "monitoring_active": monitor.running,
        "alerts_count": len(monitoring_data["alerts"]),
        "logs_count": len(monitoring_data["logs"]),
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("Starting Infotainment System - Layer 2 Data Monitoring")
    print("Available endpoints:")
    print("- GET  /api/monitor")
    print("- GET  /api/system-metrics")
    print("- GET  /api/vehicle-metrics")
    print("- GET  /api/alerts")
    print("- GET  /api/logs")
    print("- POST /api/start-monitoring")
    print("- POST /api/stop-monitoring")
    print("- GET/POST /api/config")
    print("- GET  /api/health")
    print("\nStarting server on http://localhost:5002")
    
    # Start monitoring automatically
    monitor.start_monitoring()
    
    app.run(debug=True, host='0.0.0.0', port=5002)
