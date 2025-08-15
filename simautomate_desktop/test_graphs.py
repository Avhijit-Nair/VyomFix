#!/usr/bin/env python3
"""
Test script to verify enhanced graphs functionality
"""

import sys
import os
import tempfile
import pandas as pd
import numpy as np

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_graphs():
    """Test the enhanced graph visualizer"""
    try:
        from enhanced_graphs import EnhancedGraphVisualizer
        from PyQt5.QtWidgets import QApplication
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        import matplotlib.pyplot as plt
        
        # Create QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create visualizer
        visualizer = EnhancedGraphVisualizer()
        print("✓ EnhancedGraphVisualizer created successfully")
        
        # Create test data
        test_folder = create_test_data()
        print(f"✓ Test data created in: {test_folder}")
        
        # Create canvas
        fig, ax = plt.subplots(figsize=(10, 8))
        canvas = FigureCanvas(fig)
        print("✓ Canvas created successfully")
        
        # Test graph creation
        result = visualizer.create_enhanced_graphs(test_folder, canvas)
        print("✓ Enhanced graphs created successfully")
        
        # Clean up
        import shutil
        shutil.rmtree(test_folder)
        print("✓ Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"✗ Graph test failed: {e}")
        return False

def create_test_data():
    """Create test data files"""
    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix="test_graphs_")
    
    # Create test CSV files
    time_points = np.linspace(0, 100, 200)
    
    # Chart 1: Altitude data
    altitude_real = 10000 + 500 * np.sin(time_points / 10) + np.random.normal(0, 30, 200)
    altitude_sim = 10000 + 500 * np.sin(time_points / 10) + np.random.normal(0, 20, 200)
    
    df_real_1 = pd.DataFrame({
        'Time (s)': time_points,
        'Altitude (m)': altitude_real,
        'Speed (m/s)': 250 + 20 * np.sin(time_points / 15) + np.random.normal(0, 3, 200)
    })
    
    df_sim_1 = pd.DataFrame({
        'Time (s)': time_points,
        'Altitude (m)': altitude_sim,
        'Speed (m/s)': 250 + 20 * np.sin(time_points / 15) + np.random.normal(0, 2, 200)
    })
    
    # Chart 2: Attitude data
    attitude_real = 5 + 3 * np.sin(time_points / 8) + np.random.normal(0, 0.3, 200)
    attitude_sim = 5 + 3 * np.sin(time_points / 8) + np.random.normal(0, 0.2, 200)
    
    df_real_2 = pd.DataFrame({
        'Time (s)': time_points,
        'Angle of Attack (deg)': attitude_real,
        'Lift Coefficient': 1.2 + 0.3 * np.sin(time_points / 12) + np.random.normal(0, 0.05, 200)
    })
    
    df_sim_2 = pd.DataFrame({
        'Time (s)': time_points,
        'Angle of Attack (deg)': attitude_sim,
        'Lift Coefficient': 1.2 + 0.3 * np.sin(time_points / 12) + np.random.normal(0, 0.03, 200)
    })
    
    # Chart 3: Additional data
    df_real_3 = pd.DataFrame({
        'Time (s)': time_points,
        'Acceleration (m/s²)': 9.8 + np.random.normal(0, 0.5, 200)
    })
    
    df_sim_3 = pd.DataFrame({
        'Time (s)': time_points,
        'Acceleration (m/s²)': 9.8 + np.random.normal(0, 0.3, 200)
    })
    
    # Save files
    df_real_1.to_csv(os.path.join(temp_dir, 'df_chart_1_real.csv'), index=False)
    df_sim_1.to_csv(os.path.join(temp_dir, 'df_chart_1_simulated.csv'), index=False)
    df_real_2.to_csv(os.path.join(temp_dir, 'df_chart_2_real.csv'), index=False)
    df_sim_2.to_csv(os.path.join(temp_dir, 'df_chart_2_simulated.csv'), index=False)
    df_real_3.to_csv(os.path.join(temp_dir, 'df_chart_3_real.csv'), index=False)
    df_sim_3.to_csv(os.path.join(temp_dir, 'df_chart_3_simulated.csv'), index=False)
    
    return temp_dir

def test_chat_panel():
    """Test the chat panel functionality"""
    try:
        from chat_panel import ChatPanel
        from root_cause_analyzer import RootCauseAnalyzer
        from PyQt5.QtWidgets import QApplication
        
        # Create QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create analyzer
        analyzer = RootCauseAnalyzer()
        print("✓ RootCauseAnalyzer created successfully")
        
        # Create chat panel
        chat_panel = ChatPanel(analyzer)
        print("✓ ChatPanel created successfully")
        
        # Test message sending
        test_message = "Analyze the altitude anomaly"
        response = chat_panel.generate_ai_response(test_message)
        print(f"✓ Chat response generated: {response[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Chat panel test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Enhanced Graphs and Chat Functionality")
    print("=" * 50)
    
    tests = [
        ("Enhanced Graphs Test", test_enhanced_graphs),
        ("Chat Panel Test", test_chat_panel),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
            print(f"✓ {test_name} passed")
        else:
            print(f"✗ {test_name} failed")
    
    print(f"\n{'=' * 50}")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The graphs and chat should work correctly.")
        print("\nTo test in the application:")
        print("1. Run the enhanced application: python run_enhanced.py")
        print("2. Select a report from the list")
        print("3. Check that graphs are populated")
        print("4. Go to the Chat tab and ask about anomalies")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main() 