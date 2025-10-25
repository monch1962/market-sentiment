# Use a lightweight Python 3.14 image as the base
FROM python:3.14-slim-bookworm

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /app

# Install uv, the fast Python package installer
RUN pip install uv

# Copy the requirements file and install dependencies using uv
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Download necessary NLTK data packages
# These are required for the sentiment_analysis.py script
RUN python -m nltk.downloader punkt averaged_perceptron_tagger maxent_ne_chunker words punkt_tab

# Copy the application code into the container
COPY sentiment_analysis.py .
COPY api.py .
COPY README.md .
COPY templates /app/templates

# Expose the port that FastAPI will run on
EXPOSE 8000

# Command to run the FastAPI application using Uvicorn
# --host 0.0.0.0 makes the server accessible from outside the container
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
