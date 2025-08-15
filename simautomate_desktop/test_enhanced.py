#!/usr/bin/env python3
"""
Test script for the enhanced VyomFix Desktop application
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    try:
        from main_enhanced import VyomFixDesktop
        print("✓ Successfully imported VyomFixDesktop")
        
        from root_cause_analyzer import RootCauseAnalyzer
        print("✓ Successfully imported RootCauseAnalyzer")
        
        from chat_panel import ChatPanel
        print("✓ Successfully imported ChatPanel")
        
        from enhanced_graphs import EnhancedGraphVisualizer
        print("✓ Successfully imported EnhancedGraphVisualizer")
        
        from folder_watcher import start_watching
        print("✓ Successfully imported folder_watcher")
        
        from core.pipeline import process_simulation_pdf
        print("✓ Successfully imported process_simulation_pdf")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_analyzer():
    """Test the root cause analyzer"""
    try:
        from root_cause_analyzer import RootCauseAnalyzer
        
        # Test without API key (should use fallback)
        analyzer = RootCauseAnalyzer()
        response = analyzer.analyze_anomaly("attitude deviation", "medium", 45.5, "What caused this anomaly?")
        print(f"✓ Analyzer fallback response: {response[:50]}...")
        
        return True
    except Exception as e:
        print(f"✗ Analyzer test failed: {e}")
        return False

def test_graph_visualizer():
    """Test the enhanced graph visualizer"""
    try:
        from enhanced_graphs import EnhancedGraphVisualizer
        
        visualizer = EnhancedGraphVisualizer()
        print("✓ EnhancedGraphVisualizer created successfully")
        
        return True
    except Exception as e:
        print(f"✗ Graph visualizer test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Enhanced VyomFix Desktop Application")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Analyzer Tests", test_analyzer),
        ("Graph Visualizer Tests", test_graph_visualizer),
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
        print("🎉 All tests passed! The enhanced application should work correctly.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main() 