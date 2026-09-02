"""
wsgi.py
-------
Production Web Server Gateway Interface (WSGI) entry point for Gunicorn & AWS deployment.
"""

from app import app, db

# Ensure database tables exist before serving traffic
with app.app_context():
  db.create_all()

if __name__ == "__main__":
  app.run()