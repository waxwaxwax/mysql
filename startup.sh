#!/bin/bash

# アプリケーションの起動
gunicorn --bind=0.0.0.0 --timeout 600 app:app
