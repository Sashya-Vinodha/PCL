from flask import Flask, jsonify, request
from flask_cors import CORS
import psutil
import time
import threading
from datetime import datetime, timedelta
import json
import logging
import requests

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Layer 1 integration configuration
layer1_config = {
    "url": "http://localhost:5001",
    "enabled": True,
    "timeout": 5.0
}

# Enhanced monitoring data structure
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
        "mileage": 0,
        "safety_metrics": {
            "following_distance": 0,
            "brake_pressure": 0,
            "acceleration": 0,
            "steering_angle": 0
        }
    },
    "weather_analysis": {
        "current_condition": "clear",
        "risk_assessment": "low",
        "visibility_trend": [],
        "wind_trend": [],
        "precipitation_trend": [],
        "ai_trigger_count": 0
    },
    "driver_behavior_analysis": {
        "current_alertness": "alert",
        "fatigue_trend": [],
        "stress_trend": [],
        "performance_score": 85,
        "behavior_pattern": "normal",
        "alert_frequency": 0
    },
    "ai_integration": {
        "active_triggers": [],
        "weather_warnings": 0,
        "behavior_alerts": 0,
        "safety_notifications": 0,
        "last_layer3_sync": None
    },
    "alerts": [],
    "logs": [],
    "incident": {
        "accident": False
    },
    "timestamp": datetime.now().isoformat()
}

# Enhanced monitoring configuration
monitoring_config = {
    "monitoring_enabled": True,
    "layer1_integration": True,
    "alert_thresholds": {
        "cpu_usage": 80,
        "memory_usage": 85,
        "fuel_level": 20,
        "temperature": 85,
        "speed": 90,
        "visibility": 2.0,
        "wind_speed": 20.0,
        "fatigue_score": 70,
        "following_distance": 2.0
    },
    "analysis_intervals": {
        "weather_trend": 60,  # seconds
        "behavior_trend": 30,  # seconds
        "ai_sync": 15  # seconds
    },
    "log_retention_hours": 24
}

class EnhancedDataMonitor:
    def __init__(self):
        self.running = False
        self.monitor_thread = None
        self.last_weather_analysis = datetime.now()
        self.last_behavior_analysis = datetime.now()
        self.last_ai_sync = datetime.now()
    
    def start_monitoring(self):
        """Start the enhanced monitoring thread"""
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(target=self._enhanced_monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            logger.info("Enhanced data monitoring started with Layer 1 integration")
    
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("Enhanced data monitoring stopped")
    
    def _enhanced_monitor_loop(self):
        """Enhanced monitoring loop with comprehensive data analysis"""
        while self.running:
            try:
                # Collect basic metrics
                self._collect_system_metrics()
                
                # Collect enhanced data from Layer 1
                if monitoring_config["layer1_integration"]:
                    self._collect_layer1_data()
                
                # Perform time-based analysis
                current_time = datetime.now()
                
                if (current_time - self.last_weather_analysis).seconds >= monitoring_config["analysis_intervals"]["weather_trend"]:
                    self._analyze_weather_trends()
                    self.last_weather_analysis = current_time
                
                if (current_time - self.last_behavior_analysis).seconds >= monitoring_config["analysis_intervals"]["behavior_trend"]:
                    self._analyze_driver_behavior()
                    self.last_behavior_analysis = current_time
                
                if (current_time - self.last_ai_sync).seconds >= monitoring_config["analysis_intervals"]["ai_sync"]:
                    self._sync_with_ai_layer()
                    self.last_ai_sync = current_time
                
                # Check for enhanced alerts
                self._check_enhanced_alerts()
                self._cleanup_old_logs()
                
                time.sleep(5)  # Monitor every 5 seconds
            except Exception as e:
                logger.error(f"Error in enhanced monitoring loop: {e}")
    
    def _collect_layer1_data(self):
        """Collect comprehensive data from Layer 1 simulation"""
        try:
            base_url = layer1_config["url"]
            timeout = layer1_config["timeout"]
            
            # Get vehicle data
            response = requests.get(f"{base_url}/api/vehicle-data", timeout=timeout)
            if response.status_code == 200:
                vehicle_data = response.json()
                monitoring_data["vehicle_metrics"].update({
                    "speed": vehicle_data.get("speed", 0),
                    "rpm": vehicle_data.get("rpm", 0),
                    "fuel_level": vehicle_data.get("fuel_level", 0),
                    "temperature": vehicle_data.get("temperature", 0),
                    "safety_metrics": vehicle_data.get("safety_metrics", {})
                })
                monitoring_data["incident"]["accident"] = bool(
                    vehicle_data.get("accident") or vehicle_data.get("airbag") or vehicle_data.get("airbag_deployed")
                )
            
            # Get weather data
            response = requests.get(f"{base_url}/api/weather-data", timeout=timeout)
            if response.status_code == 200:
                weather_data = response.json()
                self._update_weather_analysis(weather_data)
            
            # Get driver behavior data
            response = requests.get(f"{base_url}/api/driver-behavior", timeout=timeout)
            if response.status_code == 200:
                behavior_data = response.json()
                self._update_behavior_analysis(behavior_data)
            
            # Get AI triggers
            response = requests.get(f"{base_url}/api/ai-triggers", timeout=timeout)
            if response.status_code == 200:
                trigger_data = response.json()
                monitoring_data["ai_integration"]["active_triggers"] = trigger_data.get("triggers", [])
                monitoring_data["ai_integration"]["last_layer3_sync"] = datetime.now().isoformat()
                
        except requests.RequestException as e:
            logger.warning(f"Failed to collect Layer 1 data: {e}")
            # Fallback to local simulation
            self._collect_vehicle_metrics()
    
    def _update_weather_analysis(self, weather_data):
        """Update weather analysis with trend tracking"""
        current_condition = weather_data.get("condition", "clear")
        visibility = weather_data.get("visibility", 10.0)
        wind_speed = weather_data.get("wind_speed", 0)
        precipitation = weather_data.get("precipitation", 0)
        
        # Update current analysis
        monitoring_data["weather_analysis"]["current_condition"] = current_condition
        
        # Calculate risk assessment
        risk_factors = []
        if visibility < 2.0:
            risk_factors.append("low_visibility")
        if wind_speed > 20:
            risk_factors.append("high_winds")
        if precipitation > 3.0:
            risk_factors.append("heavy_precipitation")
        
        if len(risk_factors) >= 2:
            monitoring_data["weather_analysis"]["risk_assessment"] = "high"
        elif len(risk_factors) == 1:
            monitoring_data["weather_analysis"]["risk_assessment"] = "medium"
        else:
            monitoring_data["weather_analysis"]["risk_assessment"] = "low"
        
        # Update trends (keep last 20 readings)
        current_time = datetime.now().isoformat()
        monitoring_data["weather_analysis"]["visibility_trend"].append({
            "value": visibility,
            "timestamp": current_time
        })
        monitoring_data["weather_analysis"]["wind_trend"].append({
            "value": wind_speed,
            "timestamp": current_time
        })
        monitoring_data["weather_analysis"]["precipitation_trend"].append({
            "value": precipitation,
            "timestamp": current_time
        })
        
        # Keep only recent trends
        for trend_key in ["visibility_trend", "wind_trend", "precipitation_trend"]:
            monitoring_data["weather_analysis"][trend_key] = monitoring_data["weather_analysis"][trend_key][-20:]
    
    def _update_behavior_analysis(self, behavior_data):
        """Update driver behavior analysis with pattern recognition"""
        alertness = behavior_data.get("alertness_status", "alert")
        fatigue_score = behavior_data.get("biometric_data", {}).get("fatigue_score", 0)
        stress_level = behavior_data.get("biometric_data", {}).get("stress_level", 0)
        
        # Update current analysis
        monitoring_data["driver_behavior_analysis"]["current_alertness"] = alertness
        
        # Calculate performance score (0-100)
        performance_factors = {
            "alertness": 40 if alertness == "alert" else 20 if alertness == "drowsy" else 10,
            "fatigue": max(0, 40 - (fatigue_score * 0.4)),
            "stress": max(0, 20 - (stress_level * 0.2))
        }
        monitoring_data["driver_behavior_analysis"]["performance_score"] = sum(performance_factors.values())
        
        # Determine behavior pattern
        if fatigue_score > 70 or alertness == "drowsy":
            monitoring_data["driver_behavior_analysis"]["behavior_pattern"] = "fatigue_detected"
        elif stress_level > 70 or alertness == "distracted":
            monitoring_data["driver_behavior_analysis"]["behavior_pattern"] = "stress_detected"
        elif monitoring_data["driver_behavior_analysis"]["performance_score"] > 80:
            monitoring_data["driver_behavior_analysis"]["behavior_pattern"] = "optimal"
        else:
            monitoring_data["driver_behavior_analysis"]["behavior_pattern"] = "normal"
        
        # Update trends (keep last 20 readings)
        current_time = datetime.now().isoformat()
        monitoring_data["driver_behavior_analysis"]["fatigue_trend"].append({
            "value": fatigue_score,
            "timestamp": current_time
        })
        monitoring_data["driver_behavior_analysis"]["stress_trend"].append({
            "value": stress_level,
            "timestamp": current_time
        })
        
        # Keep only recent trends
        for trend_key in ["fatigue_trend", "stress_trend"]:
            monitoring_data["driver_behavior_analysis"][trend_key] = monitoring_data["driver_behavior_analysis"][trend_key][-20:]
    
    def _analyze_weather_trends(self):
        """Analyze weather trends and predict conditions"""
        if len(monitoring_data["weather_analysis"]["visibility_trend"]) < 3:
            return
        
        # Analyze visibility trend
        recent_visibility = [point["value"] for point in monitoring_data["weather_analysis"]["visibility_trend"][-3:]]
        if all(v < 2.0 for v in recent_visibility):
            self._log_event("Persistent low visibility detected - sustained weather warning", "WARNING")
            monitoring_data["weather_analysis"]["ai_trigger_count"] += 1
        
        # Analyze wind trend
        recent_wind = [point["value"] for point in monitoring_data["weather_analysis"]["wind_trend"][-3:]]
        if all(w > 20 for w in recent_wind):
            self._log_event("Sustained high winds detected - driving stability concern", "WARNING")
            monitoring_data["weather_analysis"]["ai_trigger_count"] += 1
    
    def _analyze_driver_behavior(self):
        """Analyze driver behavior patterns and trends"""
        if len(monitoring_data["driver_behavior_analysis"]["fatigue_trend"]) < 3:
            return
        
        # Analyze fatigue progression
        recent_fatigue = [point["value"] for point in monitoring_data["driver_behavior_analysis"]["fatigue_trend"][-3:]]
        if recent_fatigue[-1] > recent_fatigue[0] + 10:  # Fatigue increasing
            self._log_event("Driver fatigue increasing - recommend break", "WARNING")
            monitoring_data["driver_behavior_analysis"]["alert_frequency"] += 1
        
        # Check for performance degradation
        if monitoring_data["driver_behavior_analysis"]["performance_score"] < 50:
            self._log_event("Driver performance degraded - multiple factors detected", "CRITICAL")
    
    def _sync_with_ai_layer(self):
        """Sync analyzed data with AI layer for enhanced intelligence"""
        try:
            # Count active triggers by type
            active_triggers = monitoring_data["ai_integration"]["active_triggers"]
            weather_warnings = len([t for t in active_triggers if t.get("type", "").startswith("weather")])
            behavior_alerts = len([t for t in active_triggers if t.get("type", "").startswith("driver")])
            safety_notifications = len([t for t in active_triggers if t.get("type", "").startswith("safety")])
            
            monitoring_data["ai_integration"].update({
                "weather_warnings": weather_warnings,
                "behavior_alerts": behavior_alerts,
                "safety_notifications": safety_notifications
            })
            
            # Log significant AI activity
            total_triggers = len(active_triggers)
            if total_triggers > 2:
                self._log_event(f"High AI activity: {total_triggers} active triggers", "INFO")
            
        except Exception as e:
            logger.error(f"Failed to sync with AI layer: {e}")
    
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
        """Fallback vehicle metrics collection (simulation)"""
        import random
        
        # Simulate vehicle data (fallback when Layer 1 unavailable)
        monitoring_data["vehicle_metrics"] = {
            "speed": random.randint(45, 95),
            "rpm": random.randint(1800, 3200),
            "fuel_level": max(0, monitoring_data["vehicle_metrics"]["fuel_level"] - random.uniform(0, 0.1)),
            "temperature": random.randint(65, 90),
            "mileage": monitoring_data["vehicle_metrics"]["mileage"] + random.uniform(0, 0.01)
        }
    
    def _check_enhanced_alerts(self):
        """Check for enhanced alert conditions with comprehensive analysis"""
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

        # Enhanced vehicle alerts
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
                "type": "driver",
                "severity": "warning",
                "message": f"High speed detected: {monitoring_data['vehicle_metrics']['speed']} mph",
                "timestamp": datetime.now().isoformat()
            })

        # Enhanced safety alerts
        safety_metrics = monitoring_data["vehicle_metrics"].get("safety_metrics", {})
        if safety_metrics.get("following_distance", 999) < thresholds["following_distance"]:
            alerts.append({
                "type": "safety",
                "severity": "critical",
                "message": f"Following distance too close: {safety_metrics['following_distance']:.1f}s",
                "timestamp": datetime.now().isoformat()
            })

        # --- Simulation-based weather alerts ---
        sim = monitoring_data.get("simulation", {})
        distance_to_weather_event = sim.get("distance_to_weather_event", 100)
        if distance_to_weather_event < 10:
            alerts.append({
                "type": "weather",
                "severity": "critical",
                "message": "Strong weather alert: severe conditions ahead",
                "timestamp": datetime.now().isoformat()
            })
        elif distance_to_weather_event < 30:
            alerts.append({
                "type": "weather",
                "severity": "warning",
                "message": "Weather alert: rain expected ahead",
                "timestamp": datetime.now().isoformat()
            })

        # Weather-based alerts (fallback to old logic)
        weather_analysis = monitoring_data["weather_analysis"]
        if weather_analysis["current_condition"] in ["rain", "fog", "snow", "storm"]:
            alerts.append({
                "type": "weather",
                "severity": "warning",
                "message": f"Weather alert - condition: {weather_analysis['current_condition']}",
                "timestamp": datetime.now().isoformat()
            })
        elif weather_analysis["risk_assessment"] == "high":
            alerts.append({
                "type": "weather",
                "severity": "warning",
                "message": f"High weather risk detected - condition: {weather_analysis['current_condition']}",
                "timestamp": datetime.now().isoformat()
            })

        if monitoring_data.get("incident", {}).get("accident"):
            recent_accident = any(
                a.get("type") == "accident" for a in monitoring_data["alerts"][-5:]
            )
            if not recent_accident:
                alerts.append({
                    "type": "accident",
                    "severity": "critical",
                    "message": "Accident detected",
                    "timestamp": datetime.now().isoformat()
                })

        # Driver behavior alerts
        behavior_analysis = monitoring_data["driver_behavior_analysis"]
        if behavior_analysis["performance_score"] < 50:
            alerts.append({
                "type": "driver",
                "severity": "critical",
                "message": f"Driver performance degraded - score: {behavior_analysis['performance_score']}/100",
                "timestamp": datetime.now().isoformat()
            })

        if behavior_analysis["behavior_pattern"] in ["fatigue_detected", "stress_detected"]:
            alerts.append({
                "type": "driver",
                "severity": "warning",
                "message": f"Driver {behavior_analysis['behavior_pattern'].replace('_', ' ')}",
                "timestamp": datetime.now().isoformat()
            })

        # AI integration alerts
        ai_integration = monitoring_data["ai_integration"]
        total_ai_warnings = ai_integration["weather_warnings"] + ai_integration["behavior_alerts"] + ai_integration["safety_notifications"]
        if total_ai_warnings > 3:
            alerts.append({
                "type": "ai_system",
                "severity": "warning",
                "message": f"High AI activity: {total_ai_warnings} active warnings/alerts",
                "timestamp": datetime.now().isoformat()
            })

        # Add new alerts to the list
        for alert in alerts:
            monitoring_data["alerts"].append(alert)
            self._log_event(f"ALERT: {alert['message']}", alert['severity'].upper())

        # Keep only recent alerts (last 100)
        monitoring_data["alerts"] = monitoring_data["alerts"][-100:]
    
    def _log_event(self, message, level="INFO"):
        """Log an event with enhanced context"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "context": {
                "weather_risk": monitoring_data["weather_analysis"]["risk_assessment"],
                "driver_performance": monitoring_data["driver_behavior_analysis"]["performance_score"],
                "active_ai_triggers": len(monitoring_data["ai_integration"]["active_triggers"])
            }
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

# Initialize enhanced monitor
monitor = EnhancedDataMonitor()

@app.route('/')
def home():
    return jsonify({
        "message": "Enhanced Infotainment System - Layer 2 Data Monitoring", 
        "status": "running",
        "monitoring_enabled": monitoring_config["monitoring_enabled"],
        "layer1_integration": monitoring_config["layer1_integration"],
        "features": [
            "Real-time system metrics",
            "Enhanced vehicle telemetry",
            "Weather trend analysis", 
            "Driver behavior pattern recognition",
            "AI integration monitoring",
            "Comprehensive alert system"
        ],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/monitor', methods=['GET', 'POST'])
def get_monitoring_data():
    """Get all enhanced monitoring data or accept updates from Layer 1"""
    if request.method == 'GET':
        return jsonify(monitoring_data)

    data = request.get_json() or {}
    vehicle = data.get("vehicle_data", {})
    weather = data.get("weather_data", {})
    behavior = data.get("driver_behavior", {})
    incident = data.get("incident", {})

    if vehicle:
        monitoring_data["vehicle_metrics"].update({
            "speed": vehicle.get("speed", monitoring_data["vehicle_metrics"].get("speed", 0)),
            "rpm": vehicle.get("rpm", monitoring_data["vehicle_metrics"].get("rpm", 0)),
            "fuel_level": vehicle.get("fuel_level", monitoring_data["vehicle_metrics"].get("fuel_level", 0)),
            "temperature": vehicle.get("temperature", monitoring_data["vehicle_metrics"].get("temperature", 0)),
            "safety_metrics": vehicle.get("safety_metrics", monitoring_data["vehicle_metrics"].get("safety_metrics", {}))
        })

    if weather:
        self_weather = {
            "condition": weather.get("condition", monitoring_data["weather_analysis"].get("current_condition", "clear")),
            "visibility": weather.get("visibility", 10.0),
            "wind_speed": weather.get("wind_speed", 0),
            "precipitation": weather.get("precipitation", 0)
        }
        monitor._update_weather_analysis(self_weather)

    if behavior:
        monitor._update_behavior_analysis(behavior)

    if incident:
        monitoring_data["incident"]["accident"] = bool(incident.get("accident"))

    monitoring_data["timestamp"] = datetime.now().isoformat()
    return jsonify({"status": "ok", "timestamp": monitoring_data["timestamp"]})

@app.route('/api/enhanced-analysis')
def get_enhanced_analysis():
    """Get comprehensive analysis data"""
    return jsonify({
        "weather_analysis": monitoring_data["weather_analysis"],
        "driver_behavior_analysis": monitoring_data["driver_behavior_analysis"], 
        "ai_integration": monitoring_data["ai_integration"],
        "analysis_summary": {
            "overall_risk_level": _calculate_overall_risk(),
            "system_health": _calculate_system_health(),
            "recommendations": _generate_recommendations()
        },
        "timestamp": monitoring_data["timestamp"]
    })

@app.route('/api/weather-analysis')
def get_weather_analysis():
    """Get detailed weather analysis and trends"""
    return jsonify({
        "weather_analysis": monitoring_data["weather_analysis"],
        "trends_summary": {
            "visibility_avg": _calculate_trend_average("visibility_trend"),
            "wind_avg": _calculate_trend_average("wind_trend"),
            "precipitation_avg": _calculate_trend_average("precipitation_trend")
        },
        "timestamp": monitoring_data["timestamp"]
    })

@app.route('/api/driver-behavior-analysis')
def get_driver_behavior_analysis():
    """Get detailed driver behavior analysis and patterns"""
    return jsonify({
        "driver_behavior_analysis": monitoring_data["driver_behavior_analysis"],
        "performance_trend": _calculate_performance_trend(),
        "risk_factors": _identify_driver_risk_factors(),
        "timestamp": monitoring_data["timestamp"]
    })

@app.route('/api/ai-integration-status')
def get_ai_integration_status():
    """Get AI integration and trigger status"""
    return jsonify({
        "ai_integration": monitoring_data["ai_integration"],
        "layer1_connectivity": _check_layer1_connectivity(),
        "trigger_distribution": _analyze_trigger_distribution(),
        "timestamp": monitoring_data["timestamp"]
    })

def _calculate_overall_risk():
    """Calculate overall system risk level"""
    risk_factors = []
    
    # Weather risk
    if monitoring_data["weather_analysis"]["risk_assessment"] != "low":
        risk_factors.append("weather")
    
    # Driver risk
    if monitoring_data["driver_behavior_analysis"]["performance_score"] < 60:
        risk_factors.append("driver")
    
    # AI trigger risk
    if len(monitoring_data["ai_integration"]["active_triggers"]) > 2:
        risk_factors.append("multiple_triggers")
    
    # Vehicle safety risk
    safety_metrics = monitoring_data["vehicle_metrics"].get("safety_metrics", {})
    if safety_metrics.get("following_distance", 999) < 2.0:
        risk_factors.append("safety")
    
    if len(risk_factors) >= 3:
        return "critical"
    elif len(risk_factors) >= 2:
        return "high"
    elif len(risk_factors) == 1:
        return "medium"
    else:
        return "low"

def _calculate_system_health():
    """Calculate overall system health score"""
    health_score = 100
    
    # System metrics impact
    cpu_impact = max(0, monitoring_data["system_metrics"]["cpu_usage"] - 50) * 0.5
    memory_impact = max(0, monitoring_data["system_metrics"]["memory_usage"] - 60) * 0.4
    health_score -= (cpu_impact + memory_impact)
    
    # Alert frequency impact
    recent_alerts = len([a for a in monitoring_data["alerts"][-10:] if a["severity"] in ["critical", "warning"]])
    health_score -= recent_alerts * 5
    
    # AI integration health
    if monitoring_data["ai_integration"]["last_layer3_sync"] is None:
        health_score -= 10
    
    return max(0, min(100, int(health_score)))

def _generate_recommendations():
    """Generate actionable recommendations based on current data"""
    recommendations = []
    
    # Weather recommendations
    weather_risk = monitoring_data["weather_analysis"]["risk_assessment"]
    if weather_risk in ["high", "medium"]:
        recommendations.append({
            "category": "weather",
            "priority": "high" if weather_risk == "high" else "medium",
            "message": f"Weather conditions pose {weather_risk} risk - adjust driving accordingly",
            "actions": ["reduce_speed", "increase_following_distance", "monitor_visibility"]
        })
    
    # Driver behavior recommendations
    performance = monitoring_data["driver_behavior_analysis"]["performance_score"]
    if performance < 60:
        recommendations.append({
            "category": "driver",
            "priority": "high",
            "message": "Driver performance is degraded - consider taking a break",
            "actions": ["suggest_break", "enable_driver_alerts", "activate_fatigue_monitoring"]
        })
    
    # System performance recommendations
    if monitoring_data["system_metrics"]["cpu_usage"] > 80:
        recommendations.append({
            "category": "system",
            "priority": "medium",
            "message": "High system load detected - some features may be affected",
            "actions": ["optimize_performance", "close_unnecessary_apps", "monitor_resources"]
        })
    
    return recommendations

def _calculate_trend_average(trend_key):
    """Calculate average value from trend data"""
    trend_data = monitoring_data["weather_analysis"].get(trend_key, [])
    if not trend_data:
        return 0
    return sum(point["value"] for point in trend_data) / len(trend_data)

def _calculate_performance_trend():
    """Calculate driver performance trend"""
    fatigue_trend = monitoring_data["driver_behavior_analysis"]["fatigue_trend"]
    stress_trend = monitoring_data["driver_behavior_analysis"]["stress_trend"]
    
    if len(fatigue_trend) < 2 or len(stress_trend) < 2:
        return "insufficient_data"
    
    fatigue_delta = fatigue_trend[-1]["value"] - fatigue_trend[0]["value"]
    stress_delta = stress_trend[-1]["value"] - stress_trend[0]["value"]
    
    if fatigue_delta > 10 or stress_delta > 10:
        return "declining"
    elif fatigue_delta < -5 and stress_delta < -5:
        return "improving"
    else:
        return "stable"

def _identify_driver_risk_factors():
    """Identify specific driver risk factors"""
    risk_factors = []
    
    behavior = monitoring_data["driver_behavior_analysis"]
    
    if behavior["current_alertness"] != "alert":
        risk_factors.append(f"alertness_{behavior['current_alertness']}")
    
    if behavior["performance_score"] < 70:
        risk_factors.append("low_performance")
    
    if behavior["behavior_pattern"] in ["fatigue_detected", "stress_detected"]:
        risk_factors.append(behavior["behavior_pattern"])
    
    return risk_factors

def _analyze_trigger_distribution():
    """Analyze distribution of AI triggers"""
    triggers = monitoring_data["ai_integration"]["active_triggers"]
    distribution = {}
    
    for trigger in triggers:
        trigger_type = trigger.get("type", "unknown")
        category = trigger_type.split("_")[0]  # e.g., "weather", "driver", "safety"
        distribution[category] = distribution.get(category, 0) + 1
    
    return distribution

def _check_layer1_connectivity():
    """Check connectivity status with Layer 1"""
    try:
        response = requests.get(f"{layer1_config['url']}/", timeout=2)
        return {
            "status": "connected" if response.status_code == 200 else "error",
            "last_check": datetime.now().isoformat()
        }
    except:
        return {
            "status": "disconnected", 
            "last_check": datetime.now().isoformat()
        }

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
    print("Starting Enhanced Infotainment System - Layer 2 Data Monitoring")
    print("Enhanced Features:")
    print("- Real-time Layer 1 data integration")
    print("- Weather trend analysis and prediction")
    print("- Driver behavior pattern recognition") 
    print("- AI trigger monitoring and analysis")
    print("- Comprehensive risk assessment")
    print("\nAvailable endpoints:")
    print("- GET  /api/monitor (all data)")
    print("- GET  /api/enhanced-analysis")
    print("- GET  /api/weather-analysis")
    print("- GET  /api/driver-behavior-analysis")
    print("- GET  /api/ai-integration-status")
    print("- GET  /api/system-metrics")
    print("- GET  /api/vehicle-metrics")
    print("- GET  /api/alerts")
    print("- GET  /api/logs")
    print("- POST /api/start-monitoring")
    print("- POST /api/stop-monitoring")
    print("- GET/POST /api/config")
    print("- GET  /api/health")
    print("\nStarting server on http://localhost:5002")
    print("Layer 1 integration:", "ENABLED" if layer1_config["enabled"] else "DISABLED")
    
    # Start enhanced monitoring automatically
    monitor.start_monitoring()
    
    app.run(debug=True, host='0.0.0.0', port=5002)
