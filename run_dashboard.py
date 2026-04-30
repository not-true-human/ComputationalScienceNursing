#!/usr/bin/env python
"""
Launch script for the STI Knowledge Research Dashboard
"""
import sys
import os

# Add roaming Python packages to path
roaming_path = os.path.expanduser(r'~\AppData\Roaming\Python\Python314\site-packages')
if roaming_path not in sys.path:
    sys.path.insert(0, roaming_path)

import streamlit.web.cli as stcli

if __name__ == '__main__':
    sys.argv = ['streamlit', 'run', 'app.py', '--server.headless', 'false']
    stcli.main()