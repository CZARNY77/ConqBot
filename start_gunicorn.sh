#!/bin/bash
/home/container/.local/bin/gunicorn --workers 3 --bind 0.0.0.0:2005 app:app
