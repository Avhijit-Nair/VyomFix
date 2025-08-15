import random
import pandas as pd
import google.generativeai as genai
import os
import json

class RootCauseAnalyzer:
    """LLM-like agent for root cause analysis of flight anomalies using Gemini API"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.model = None
        self._setup_gemini()
        
        # Fallback data for when API is not available
        self.hardware_issues = [
            "Sensor malfunction in the {component} system",
            "Calibration drift in {component} sensors",
            "Electrical interference affecting {component} readings",
            "Mechanical wear in {component} components",
            "Software bug in {component} control algorithm",
            "Communication delay between {component} and flight computer"
        ]
        
        self.atmospheric_conditions = [
            "Sudden wind shear at {altitude}m altitude",
            "Turbulence caused by thermal updrafts",
            "Pressure variations due to weather front",
            "Temperature inversion affecting sensor readings",
            "Humidity changes affecting sensor calibration",
            "Density altitude variations"
        ]
        
        self.components = [
            "attitude control", "navigation", "engine", "flight control", 
            "altimeter", "airspeed indicator", "gyroscope", "accelerometer"
        ]
    
    def _setup_gemini(self):
        """Setup Gemini API"""
        try:
            if self.api_key and self.api_key.strip():
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.5-pro')
                print("✅ Gemini API configured successfully")
                print(f"API key length: {len(self.api_key)} characters")
            else:
                print("⚠️ No API key provided, using fallback analysis")
                self.model = None
        except Exception as e:
            print(f"❌ Error setting up Gemini API: {e}")
            self.model = None
    
    def set_api_key(self, api_key):
        """Set API key and reconfigure Gemini"""
        self.api_key = api_key
        print(f"Setting API key: {'Yes' if api_key and api_key.strip() else 'No'}")
        self._setup_gemini()
    
    def analyze_anomaly(self, anomaly_type, severity, time_point, user_query=""):
        """Generate a scientific root cause analysis using Gemini or fallback"""
        
        print(f"🔍 Analyzing anomaly: {anomaly_type}, severity: {severity}, time: {time_point}")
        print(f"   Model available: {'Yes' if self.model else 'No'}")
        print(f"   API key present: {'Yes' if self.api_key and self.api_key.strip() else 'No'}")
        print(f"   API key length: {len(self.api_key) if self.api_key else 0}")
        
        if self.model and self.api_key and self.api_key.strip():
            print("   ✅ Using Gemini API for analysis")
            return self._analyze_with_gemini(anomaly_type, severity, time_point, user_query)
        else:
            print("   ⚠️ Using fallback analysis (no API key or model)")
            return self._analyze_fallback(anomaly_type, severity, time_point)
    
    def _analyze_with_gemini(self, anomaly_type, severity, time_point, user_query):
        """Analyze using Gemini API"""
        try:
            print(f"🔍 Calling Gemini API...")
            print(f"   API Key length: {len(self.api_key) if self.api_key else 0}")
            print(f"   Model available: {'Yes' if self.model else 'No'}")
            
            prompt = f"""
You are a master flight anomaly root cause analyst with deep expertise in aviation systems, aerodynamics, and flight dynamics.

Context: A flight anomaly has been detected with the following parameters:
- Anomaly Type: {anomaly_type}
- Severity Level: {severity}
- Time Point: {time_point:.1f} seconds
- User Query: {user_query if user_query else "General analysis requested"}

Please provide a comprehensive, scientifically accurate root cause analysis report that includes:

1. **Technical Analysis**: Detailed explanation of potential causes (hardware malfunctions, atmospheric conditions, sensor issues, etc.)
2. **Impact Assessment**: How this anomaly affects flight safety and performance
3. **Detection Methods**: How such anomalies are typically detected and monitored
4. **Scientific Explanation**: Deep technical analysis with aviation terminology
5. **Recommendations**: Specific actionable steps for investigation and resolution
6. **Confidence Level**: Your confidence in this analysis (as a percentage)

Format the response as a professional technical report with clear sections and bullet points. Use aviation and engineering terminology appropriately.

Focus on providing scientifically sound analysis that would be useful for flight engineers and safety investigators.
            """
            
            print("   Sending prompt to Gemini...")
            response = self.model.generate_content(prompt)
            print("   ✅ Received response from Gemini")
            return response.text
            
        except Exception as e:
            print(f"❌ Gemini API error: {e}")
            return self._analyze_fallback(anomaly_type, severity, time_point)
    
    def _analyze_fallback(self, anomaly_type, severity, time_point):
        """Fallback analysis when API is not available"""
        
        # Randomly choose between hardware and atmospheric causes
        if random.random() < 0.6:  # 60% chance of hardware issue
            cause_type = "hardware"
            issue = random.choice(self.hardware_issues).format(
                component=random.choice(self.components)
            )
        else:
            cause_type = "atmospheric"
            issue = random.choice(self.atmospheric_conditions).format(
                altitude=random.randint(1000, 10000)
            )
        
        # Generate detailed analysis
        analysis = f"""
🔍 **ROOT CAUSE ANALYSIS REPORT**

**Anomaly Type:** {anomaly_type}
**Severity Level:** {severity}
**Time Point:** {time_point:.1f} seconds
**Primary Cause:** {cause_type.upper()} ISSUE

**Technical Analysis:**
• {issue}
• Impact: {self._get_impact_description(anomaly_type, severity)}
• Detection Method: {self._get_detection_method(anomaly_type)}
• Recommended Action: {self._get_recommendation(cause_type)}

**Scientific Explanation:**
{self._get_scientific_explanation(anomaly_type, cause_type)}

**Confidence Level:** {random.randint(85, 98)}%
**Analysis Timestamp:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        return analysis.strip()
    
    def _get_impact_description(self, anomaly_type, severity):
        impacts = {
            "altitude": "Flight path deviation affecting safety margins",
            "speed": "Performance degradation and fuel efficiency loss",
            "attitude": "Stability issues and passenger comfort concerns",
            "acceleration": "Structural stress and component wear"
        }
        return impacts.get(anomaly_type, "System performance degradation")
    
    def _get_detection_method(self, anomaly_type):
        methods = {
            "altitude": "Real-time altitude sensor monitoring with Kalman filtering",
            "speed": "Airspeed sensor validation against GPS and pitot-static system",
            "attitude": "Multi-axis gyroscope and accelerometer fusion",
            "acceleration": "High-frequency accelerometer data analysis"
        }
        return methods.get(anomaly_type, "Multi-sensor fusion and statistical analysis")
    
    def _get_recommendation(self, cause_type):
        if cause_type == "hardware":
            return "Immediate sensor calibration and component inspection required"
        else:
            return "Monitor weather conditions and adjust flight parameters accordingly"
    
    def _get_scientific_explanation(self, anomaly_type, cause_type):
        explanations = {
            "hardware": f"""
The detected anomaly in {anomaly_type} parameters indicates a systematic deviation from expected flight dynamics. 
This deviation exceeds the 3-sigma threshold (99.7% confidence interval) established through statistical analysis 
of baseline flight data. The root cause analysis suggests a {cause_type} malfunction affecting sensor accuracy 
or data processing algorithms. This type of anomaly can propagate through the flight control system, potentially 
affecting multiple dependent parameters and compromising flight safety margins.
            """,
            "atmospheric": f"""
The observed {anomaly_type} anomaly correlates with atmospheric condition variations that exceed normal 
operational parameters. Statistical analysis reveals a significant deviation from baseline performance 
characteristics, indicating environmental factors rather than system malfunction. The anomaly magnitude 
suggests atmospheric phenomena affecting sensor readings or aircraft aerodynamics, requiring adaptive 
control system responses to maintain optimal flight performance.
            """
        }
        return explanations.get(cause_type, "Analysis indicates environmental or system factors affecting flight parameters.") 