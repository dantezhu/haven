#!/bin/sh

gunicorn -c gun_config.py server:app
