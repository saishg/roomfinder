#!/bin/sh

PYTHONPATH=. gunicorn --config=CONFIG service.webserver:APP
