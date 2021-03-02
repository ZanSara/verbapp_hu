#! /var/www/verbapp/venv/bin/python3

import logging
import sys
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/var/www/verbapp/venv/lib/python3.6/site-packages')
sys.path.insert(0, '/var/www/verbapp')

from app import app as application

if __name__ == "__main__":
    application.run(debug=False, host="0.0.0.0")

