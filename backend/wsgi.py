# wsgi.py
# WSGI entry point for Vercel deployment
# Full path: C:\Users\Peace\Desktop\skulcbt-website\backend\wsgi.py
#
# ============================================
# AUTHOR: Emmanuel Adekunle Peace
# WEBSITE: www.emmanueladekunlepeace.com
# PHONE: 07032977572
# EMAIL: emmanueladekunlep@gmail.com
# ============================================

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app
from agent_app import app

# Vercel expects a variable named 'app'
application = app