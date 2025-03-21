# Use Python base image
FROM python:3.10

# Set working directory
WORKDIR /app

# Install dependencies
COPY review_agent/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Execute review script
CMD ["python", "review_agent/main.py"]
