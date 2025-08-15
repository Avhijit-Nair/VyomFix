#!/usr/bin/env python3
"""
Final test script to verify both graph display and chat functionality
"""

import sys
import os
import pandas as pd
import numpy as np

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_graph_data():
    """Test if graph data files exist and are readable"""
    print("🔍 Testing graph data files...")
    
    # Check if reports directory exists
    reports_dir = "data/reports"
    if not os.path.exists(reports_dir):
        print("❌ Reports directory not found")
        return False
    
    # List all report folders
    report_folders = [f for f in os.listdir(reports_dir) if os.path.isdir(os.path.join(reports_dir, f))]
    if not report_folders:
        print("❌ No report folders found")
        return False
    
    print(f"✅ Found {len(report_folders)} report folders")
    
    # Test the latest report
    latest_report = sorted(report_folders)[-1]
    report_path = os.path.join(reports_dir, latest_report)
    print(f"   Testing latest report: {latest_report}")
    
    # Check for data files
    data_files = []
    for i in range(1, 4):  # Check for 3 charts
        real_file = os.path.join(report_path, f"df_chart_{i}_real.csv")
        sim_file = os.path.join(report_path, f"df_chart_{i}_simulated.csv")
        
        if os.path.exists(real_file) and os.path.exists(sim_file):
            data_files.append((real_file, sim_file))
            print(f"   ✅ Chart {i} data files found")
        else:
            print(f"   ❌ Chart {i} data files missing")
    
    if not data_files:
        print("❌ No data files found")
        return False
    
    # Test reading the data
    try:
        real_file, sim_file = data_files[0]
        df_real = pd.read_csv(real_file)
        df_sim = pd.read_csv(sim_file)
        
        print(f"   ✅ Successfully read data files")
        print(f"   Real data shape: {df_real.shape}")
        print(f"   Sim data shape: {df_sim.shape}")
        print(f"   Real columns: {list(df_real.columns)}")
        
        return True
    except Exception as e:
        print(f"❌ Error reading data files: {e}")
        return False

def test_chat_functionality():
    """Test chat functionality"""
    print("\n🔍 Testing chat functionality...")
    
    try:
        from root_cause_analyzer import RootCauseAnalyzer
        
        # Test without API key (fallback)
        print("   Testing fallback analysis...")
        analyzer = RootCauseAnalyzer(api_key=None)
        result = analyzer.analyze_anomaly("altitude", "High", 45.5, "Test query")
        print("   ✅ Fallback analysis working")
        
        # Test with empty API key
        print("   Testing with empty API key...")
        analyzer2 = RootCauseAnalyzer(api_key="")
        result2 = analyzer2.analyze_anomaly("speed", "Medium", 30.0, "Another test")
        print("   ✅ Empty API key handling working")
        
        return True
    except Exception as e:
        print(f"❌ Error testing chat functionality: {e}")
        return False

def test_enhanced_app():
    """Test the enhanced application components"""
    print("\n🔍 Testing enhanced application components...")
    
    try:
        from enhanced_graphs import EnhancedGraphVisualizer
        from chat_panel import ChatPanel
        from root_cause_analyzer import RootCauseAnalyzer
        
        # Test graph visualizer
        print("   Testing graph visualizer...")
        visualizer = EnhancedGraphVisualizer()
        print("   ✅ Graph visualizer initialized")
        
        # Test chat panel
        print("   Testing chat panel...")
        analyzer = RootCauseAnalyzer()
        chat = ChatPanel(analyzer)
        print("   ✅ Chat panel initialized")
        
        return True
    except Exception as e:
        print(f"❌ Error testing enhanced components: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Running final fixes verification...")
    print("=" * 50)
    
    # Test graph data
    graph_ok = test_graph_data()
    
    # Test chat functionality
    chat_ok = test_chat_functionality()
    
    # Test enhanced components
    components_ok = test_enhanced_app()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print(f"   Graph Data: {'✅ PASS' if graph_ok else '❌ FAIL'}")
    print(f"   Chat Functionality: {'✅ PASS' if chat_ok else '❌ FAIL'}")
    print(f"   Enhanced Components: {'✅ PASS' if components_ok else '❌ FAIL'}")
    
    if graph_ok and chat_ok and components_ok:
        print("\n🎉 All tests passed! The enhanced application should work properly.")
        print("\n📋 Next steps:")
        print("   1. Run: python run_enhanced.py")
        print("   2. Configure Gemini API key in Admin panel")
        print("   3. Select a report to view graphs")
        print("   4. Use the chat panel for analysis")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
    
    return graph_ok and chat_ok and components_ok

if __name__ == "__main__":
    main() 