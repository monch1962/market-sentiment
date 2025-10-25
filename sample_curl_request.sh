#!/bin/bash

# This script sends a POST request to the FastAPI /scan endpoint
# to get the sentiment analysis for 'gold' news from the last 5 days.
# The JSON payload is read from payload.json to avoid shell escaping issues.

curl -X POST "http://127.0.0.1:8000/scan" \
     -H "Content-Type: application/json" \
     -d @payload.json