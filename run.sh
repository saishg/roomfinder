#!/bin/sh

PYTHONPATH=. gunicorn --config=CONFIG service.webserver:app
