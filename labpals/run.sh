#!/usr/bin/env bash

export FLASK_APP=app.py
export FLASK_ENV=development
export ELASTICSEARCH_URL=localhost:9200
flask run