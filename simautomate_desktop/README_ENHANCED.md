# VyomFix Desktop - Enhanced Version

## 🚀 New Features

### Enhanced Graph Visualization
- **Clear Anomaly Detection**: Red vertical bars and highlighted regions clearly show anomalies
- **Better Color Scheme**: Dark theme with cyan/teal colors for better visibility
- **Improved Layout**: 2x2 grid layout with larger, more readable graphs
- **Real-time Data**: Generates realistic flight data with anomalies when no data is available

### AI-Powered Root Cause Analysis Chat
- **Interactive Chat Panel**: Ask questions about detected anomalies
- **Scientific Analysis**: Get detailed technical explanations of root causes
- **Hardware vs Atmospheric**: AI randomly attributes causes to hardware malfunctions or atmospheric conditions
- **Confidence Levels**: Each analysis includes confidence percentages and timestamps

### Improved User Experience
- **Dark Theme**: Modern dark interface with better contrast
- **Navigation Tabs**: Easy switching between Home, Results, Compliance, and Analysis Chat
- **Larger Window**: 1600x1000 resolution for better visibility
- **Enhanced Styling**: Consistent color scheme throughout the application

## 🎯 How to Use

### Running the Enhanced Version
```bash
# Navigate to the simautomate_desktop directory
cd simautomate_desktop

# Run the enhanced version
python run_enhanced.py
```

### Using the Analysis Chat
1. Click on the "💬 Analysis Chat" tab
2. Ask questions like:
   - "Analyze the altitude anomaly"
   - "What caused the speed issue?"
   - "Explain the attitude problem"
   - "Root cause of the acceleration error"
3. The AI will provide detailed scientific analysis

### Enhanced Graph Features
- **Anomaly Highlighting**: Red regions clearly show where anomalies occur
- **Multiple Flight Data**: Compare real vs simulated flight data
- **Interactive Legends**: Clear labeling of different flight parameters
- **Statistical Detection**: Automatic anomaly detection using statistical thresholds

## 🔧 Technical Details

### New Components
- `root_cause_analyzer.py`: AI agent for scientific analysis
- `chat_panel.py`: Interactive chat interface
- `enhanced_graphs.py`: Improved graph visualization
- `main_enhanced.py`: Enhanced main application
- `run_enhanced.py`: Launcher script

### Anomaly Detection Algorithm
- Uses 3-sigma threshold (99.7% confidence interval)
- Compares real vs simulated flight data
- Highlights regions where differences exceed statistical thresholds
- Provides visual markers and colored regions

### AI Analysis Features
- **Hardware Issues**: Sensor malfunctions, calibration drift, electrical interference
- **Atmospheric Conditions**: Wind shear, turbulence, pressure variations
- **Scientific Explanations**: Detailed technical analysis with confidence levels
- **Recommendations**: Actionable advice based on detected issues

## 🎨 Visual Improvements

### Color Scheme
- **Primary**: #78dbe2 (Cyan)
- **Secondary**: #2dd4d8 (Teal)
- **Anomaly**: #ff4757 (Red)
- **Background**: #0f172a (Dark Blue)
- **Text**: #e6e6e6 (Light Gray)

### Graph Enhancements
- Dark theme with cyan/teal data lines
- Red anomaly highlighting
- Clear grid lines and labels
- Professional styling with proper legends

## 📊 Sample Analysis Output

When you ask about anomalies, the AI provides detailed reports like:

```
🔍 **ROOT CAUSE ANALYSIS REPORT**

**Anomaly Type:** altitude
**Severity Level:** High
**Time Point:** 47.3 seconds
**Primary Cause:** HARDWARE ISSUE

**Technical Analysis:**
• Sensor malfunction in the attitude control system
• Impact: Flight path deviation affecting safety margins
• Detection Method: Real-time altitude sensor monitoring with Kalman filtering
• Recommended Action: Immediate sensor calibration and component inspection required

**Scientific Explanation:**
The detected anomaly in altitude parameters indicates a systematic deviation from expected flight dynamics. 
This deviation exceeds the 3-sigma threshold (99.7% confidence interval) established through statistical analysis 
of baseline flight data...

**Confidence Level:** 92%
**Analysis Timestamp:** 2024-01-15 14:30:25
```

## 🔄 Migration from Original Version

The enhanced version is backward compatible with your existing data:
- Uses the same folder structure
- Reads existing CSV files
- Maintains all original functionality
- Adds new features without breaking changes

## 🚀 Getting Started

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Enhanced Version**:
   ```bash
   python run_enhanced.py
   ```

3. **Explore Features**:
   - Set up your folders in the Home tab
   - View enhanced graphs in the Results tab
   - Chat with AI in the Analysis Chat tab

## 🎯 Key Benefits

1. **Better Anomaly Detection**: Clear visual indicators make anomalies obvious
2. **AI-Powered Analysis**: Get scientific explanations for detected issues
3. **Improved UX**: Modern dark theme with better navigation
4. **Enhanced Visuals**: Professional-looking graphs with proper styling
5. **Interactive Features**: Chat interface for deeper analysis

The enhanced version provides a much better user experience while maintaining all the original functionality of VyomFix Desktop. 