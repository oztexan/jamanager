#!/bin/bash

# Activate the correct pyenv environment
eval "$(pyenv init -)"
pyenv activate jv3.11.11

# Change to backend directory
cd backend

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
