# VyomFix Compliance Automation Desktop (PyQt5)

This is the Windows desktop version of the VyomFix aircraft compliance automation software, built with PyQt5.

## Features
- Select baseline and compliance manual folders (one-time setup)
- List and open past compliance reports
- (To be implemented) Listen for new simulation data and process automatically

## Setup

1. Install Python 3.8+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python main.py
   ```

## Directory Structure
- `config.json` — Stores user-selected folders
- `data/reports/` — Stores versioned compliance reports

## Next Steps
- Integrate data listener for simulation data
- Refactor and integrate core processing logic
- Implement report versioning and management 