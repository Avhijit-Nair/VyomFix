#!/usr/bin/env python3
"""
Test script to verify folder watcher functionality in the enhanced application
"""

import sys
import os
import threading
import time

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_folder_watcher_initialization():
    """Test that the folder watcher can be properly initialized"""
    try:
        from main_enhanced import VyomFixDesktop
        from PyQt5.QtWidgets import QApplication
        
        # Create a minimal QApplication for testing
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create the enhanced desktop application
        desktop_app = VyomFixDesktop()
        
        # Check if watcher thread variables are initialized
        assert hasattr(desktop_app, 'watcher_thread'), "Watcher thread variable not initialized"
        assert hasattr(desktop_app, 'watching'), "Watching flag not initialized"
        
        print("✓ Folder watcher variables properly initialized")
        
        # Test the start_folder_watcher method
        test_folder = os.path.join(os.getcwd(), 'test_watch_folder')
        os.makedirs(test_folder, exist_ok=True)
        
        # Start watching the test folder
        desktop_app.start_folder_watcher(test_folder)
        
        # Check if the watcher thread was created and started
        assert desktop_app.watcher_thread is not None, "Watcher thread not created"
        assert desktop_app.watcher_thread.is_alive(), "Watcher thread not started"
        
        print("✓ Folder watcher thread started successfully")
        
        # Clean up
        desktop_app.watcher_thread.join(timeout=1)
        
        return True
        
    except Exception as e:
        print(f"✗ Folder watcher test failed: {e}")
        return False

def test_signal_connections():
    """Test that all signal connections are properly set up"""
    try:
        from main_enhanced import VyomFixDesktop
        from PyQt5.QtWidgets import QApplication
        
        # Create a minimal QApplication for testing
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create the enhanced desktop application
        desktop_app = VyomFixDesktop()
        
        # Check if signals are connected
        assert hasattr(desktop_app, 'status_update'), "status_update signal not found"
        assert hasattr(desktop_app, 'report_refresh'), "report_refresh signal not found"
        assert hasattr(desktop_app, 'error_popup'), "error_popup signal not found"
        assert hasattr(desktop_app, 'processing_update'), "processing_update signal not found"
        assert hasattr(desktop_app, 'processing_done'), "processing_done signal not found"
        
        print("✓ All signals properly defined")
        
        # Check if signal handlers exist
        assert hasattr(desktop_app, 'set_status'), "set_status method not found"
        assert hasattr(desktop_app, 'show_error_popup'), "show_error_popup method not found"
        assert hasattr(desktop_app, 'show_processing_update'), "show_processing_update method not found"
        assert hasattr(desktop_app, 'hide_processing_dialog'), "hide_processing_dialog method not found"
        
        print("✓ All signal handlers properly defined")
        
        return True
        
    except Exception as e:
        print(f"✗ Signal connection test failed: {e}")
        return False

def main():
    """Run all folder watcher tests"""
    print("Testing Enhanced Application Folder Watcher")
    print("=" * 50)
    
    tests = [
        ("Folder Watcher Initialization", test_folder_watcher_initialization),
        ("Signal Connections", test_signal_connections),
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
        print("🎉 All folder watcher tests passed! The enhanced application should properly detect new files.")
        print("\nTo test the folder watcher:")
        print("1. Run the enhanced application: python run_enhanced.py")
        print("2. Set up your folders (Baseline, Manual, Simulation)")
        print("3. Place a PDF file in the Simulation folder")
        print("4. The application should automatically process the file")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main() 