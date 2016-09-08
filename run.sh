#!/bin/sh

PYTHONPATH=. gunicorn --config=gunicorn.cfg service.webserver:APP
