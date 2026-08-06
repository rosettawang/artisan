#!/usr/bin/env python3
"""
Artisan Profile Designer Launcher

This script launches the standalone Artisan Profile Designer
without needing to open the main Artisan application.

Usage: python launch_profile_designer.py
"""

import sys
import os

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

def main():
    """Launch the Profile Designer"""
    try:
        from artisanlib.designer import main_standalone as designer_main
        designer_main()
    except ImportError as e:
        print(f"Error importing Profile Designer: {e}")
        print("Make sure you're running this from the Artisan directory")
        sys.exit(1)
    except Exception as e:
        print(f"Error launching Profile Designer: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()