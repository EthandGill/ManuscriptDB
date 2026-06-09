# ============================================================================
#  PythonAnywhere WSGI configuration for ManuscriptDB
# ----------------------------------------------------------------------------
#  Do NOT just leave this file in the project. PythonAnywhere ignores files in
#  your project folder for WSGI — it uses ONE specific file under /var/www/.
#
#  On the PythonAnywhere "Web" tab, click the "WSGI configuration file" link
#  (it's named like  /var/www/<username>_pythonanywhere_com_wsgi.py ), DELETE
#  everything in it, and PASTE the contents of this file. Then change the one
#  line marked below to your real username, Save, and hit "Reload".
# ============================================================================

import sys

# --- 1. Point Python at your project folder -------------------------------
#  Replace YOURUSERNAME with your PythonAnywhere username.
#  (If you uploaded the project somewhere other than ~/ManuscriptDB, fix the
#   path to match.)
project_home = "/home/YOURUSERNAME/ManuscriptDB"
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# --- 2. Import the Flask app -----------------------------------------------
#  app.py defines:  app = Flask(__name__)
#  WSGI servers look for a variable called "application", so we alias it.
from app import app as application
