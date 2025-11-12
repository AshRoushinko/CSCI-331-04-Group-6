#!/usr/bin/env python3
"""
PyQt6 Installation Test Script
Run this to verify PyQt6 is properly installed before running the main application
"""

import sys
import platform

print("=" * 60)
print("PyQt6 Installation Test")
print("=" * 60)
print(f"Python Version: {sys.version}")
print(f"Platform: {platform.system()} {platform.machine()}")
print(f"macOS Version: {platform.mac_ver()[0] if platform.system() == 'Darwin' else 'N/A'}")
print("=" * 60)

# Test imports
test_results = []

# Test PyQt6 core modules
try:
    from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton

    test_results.append(("PyQt6.QtWidgets", "✅ Success"))

    # Get PyQt6 version
    from PyQt6.QtCore import QT_VERSION_STR, PYQT_VERSION_STR

    test_results.append(("Qt Version", f"✅ {QT_VERSION_STR}"))
    test_results.append(("PyQt Version", f"✅ {PYQT_VERSION_STR}"))
except ImportError as e:
    test_results.append(("PyQt6.QtWidgets", f"❌ Failed: {e}"))

try:
    from PyQt6.QtCore import Qt, QThread, pyqtSignal

    test_results.append(("PyQt6.QtCore", "✅ Success"))
except ImportError as e:
    test_results.append(("PyQt6.QtCore", f"❌ Failed: {e}"))

try:
    from PyQt6.QtGui import QFont, QPalette, QColor, QAction

    test_results.append(("PyQt6.QtGui", "✅ Success"))
except ImportError as e:
    test_results.append(("PyQt6.QtGui", f"❌ Failed: {e}"))

# Test matplotlib backend
try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT

    test_results.append(("Matplotlib Qt Backend", "✅ Success"))
except ImportError as e:
    test_results.append(("Matplotlib Qt Backend", f"❌ Failed: {e}"))

try:
    import matplotlib

    test_results.append(("Matplotlib Version", f"✅ {matplotlib.__version__}"))
except ImportError as e:
    test_results.append(("Matplotlib", f"❌ Failed: {e}"))

try:
    import numpy

    test_results.append(("NumPy Version", f"✅ {numpy.__version__}"))
except ImportError as e:
    test_results.append(("NumPy", f"❌ Failed: {e}"))

# Print results
print("\nTest Results:")
print("-" * 60)
for module, status in test_results:
    print(f"{module:.<30} {status}")

# Check if all tests passed
all_passed = all("✅" in status for _, status in test_results)

print("=" * 60)
if all_passed:
    print("🎉 All tests passed! PyQt6 is properly installed.")
    print("You can now run your gui_app_qt6.py file.")

    # Try to create a minimal PyQt6 window to ensure it works
    print("\nTesting GUI creation...")
    try:
        app = QApplication(sys.argv)
        window = QMainWindow()
        window.setWindowTitle("PyQt6 Test")
        window.setGeometry(100, 100, 400, 300)

        button = QPushButton("Test Button", window)
        button.setGeometry(150, 120, 100, 40)

        print("✅ GUI objects created successfully!")
        print("   (Not displaying window in test mode)")

    except Exception as e:
        print(f"❌ GUI creation failed: {e}")
else:
    print("❌ Some tests failed. Please install missing packages:")
    print("\nRun this command to install all requirements:")
    print("  pip install PyQt6 matplotlib numpy")
    print("\nOr if using the requirements.txt file:")
    print("  pip install -r requirements.txt")
    print("\nFor M1/M2 Macs, you might need:")
    print("  arch -arm64 pip install PyQt6 matplotlib numpy")

print("=" * 60)