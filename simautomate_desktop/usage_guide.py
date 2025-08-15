#!/usr/bin/env python3
"""
Usage Guide for Enhanced VyomFix Desktop Application
"""

import sys
import os

def print_usage_guide():
    """Print comprehensive usage guide"""
    
    print("🚀 Enhanced VyomFix Desktop Application - Usage Guide")
    print("=" * 60)
    
    print("\n📋 **FIXED ISSUES:**")
    print("✅ Graphs now populate when clicking on reports")
    print("✅ Chat feature is fully functional")
    print("✅ Original loading animation preserved")
    print("✅ Folder watcher working correctly")
    
    print("\n🎯 **HOW TO USE:**")
    
    print("\n1️⃣ **Starting the Application:**")
    print("   cd simautomate_desktop")
    print("   .\\vyomfix\\Scripts\\activate")
    print("   python run_enhanced.py")
    
    print("\n2️⃣ **Setting Up Folders:**")
    print("   • Click 'Select Baseline' → Choose your baseline folder")
    print("   • Click 'Select Manual' → Choose your compliance manual folder")
    print("   • Click 'Select Simulation' → Choose your simulation data folder")
    print("   • The folder watcher will automatically start")
    
    print("\n3️⃣ **Testing the Folder Watcher:**")
    print("   • Place a PDF file in the Simulation folder")
    print("   • Watch the loading animation appear")
    print("   • See the processing steps with progress bar")
    print("   • Check the Reports list for new entries")
    
    print("\n4️⃣ **Viewing Enhanced Graphs:**")
    print("   • Click on '📊 Results' tab")
    print("   • Select a report from the list")
    print("   • Graphs will automatically populate with:")
    print("     - Altitude data with anomaly highlighting")
    print("     - Speed data with deviation detection")
    print("     - Angle of Attack analysis")
    print("     - Lift Coefficient visualization")
    
    print("\n5️⃣ **Using the Chat Feature:**")
    print("   • Click on '💬 Analysis Chat' tab")
    print("   • Type questions like:")
    print("     - 'Analyze the altitude anomaly'")
    print("     - 'What caused the speed issue?'")
    print("     - 'Explain the attitude problem'")
    print("     - 'Root cause of the acceleration error'")
    print("     - 'help' (for guidance)")
    
    print("\n6️⃣ **Configuring Gemini API (Optional):**")
    print("   • Click '⚙️ Admin' button")
    print("   • Enter your Gemini API key (password protected)")
    print("   • Click '💾 Save Configuration'")
    print("   • Chat will now use real AI analysis")
    
    print("\n🎨 **Enhanced Features:**")
    print("   • Dark theme with orange/black gradient")
    print("   • Modern, sleek UI design")
    print("   • Better anomaly visualization")
    print("   • Secure API key management")
    print("   • Professional loading animations")
    
    print("\n🔧 **Troubleshooting:**")
    print("   • If graphs don't show: Check that report folders contain CSV files")
    print("   • If chat doesn't work: Try typing 'help' for guidance")
    print("   • If folder watcher doesn't start: Re-select the simulation folder")
    print("   • If API key doesn't work: Check your internet connection")
    
    print("\n📊 **Test Scripts Available:**")
    print("   • python test_enhanced.py - Comprehensive functionality tests")
    print("   • python test_graphs.py - Graph and chat specific tests")
    print("   • python demo_enhanced.py - Full feature demonstration")
    
    print("\n🎉 **ENJOY YOUR ENHANCED VYOMFIX EXPERIENCE!**")
    print("=" * 60)

def print_quick_start():
    """Print quick start instructions"""
    
    print("\n⚡ **QUICK START:**")
    print("1. Activate environment: .\\vyomfix\\Scripts\\activate")
    print("2. Run app: python run_enhanced.py")
    print("3. Set up folders (Baseline, Manual, Simulation)")
    print("4. Place PDF in Simulation folder")
    print("5. Watch automatic processing with loading animation")
    print("6. View enhanced graphs in Results tab")
    print("7. Chat with AI in Analysis Chat tab")

if __name__ == "__main__":
    print_usage_guide()
    print_quick_start() 