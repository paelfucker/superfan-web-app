 #!/usr/bin/env bash
+set -euo pipefail
 
+# Create and activate virtual environment if needed
+if [ ! -d "env" ]; then
+  python3 -m venv env
+fi
 source env/bin/activate
 
 # Install Python dependencies
+pip install --upgrade pip
+pip install -r requirements.txt
 

+# Use provided PORT or default to 8000
+PORT="${PORT:-8000}"
 
 # Start FastAPI app with gunicorn
+exec gunicorn backend.main:app --bind "0.0.0.0:${PORT}"
