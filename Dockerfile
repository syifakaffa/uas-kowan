FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY templates/ templates/

# Note: For production deployment with email, set these environment variables:
# - EMAIL_HOST (default: smtp.gmail.com)
# - EMAIL_PORT (default: 587)
# - EMAIL_USER (your email)
# - EMAIL_PASSWORD (your app password)
# 
# Example Docker run:
# docker run -e EMAIL_USER=your@gmail.com -e EMAIL_PASSWORD=yourpass ...

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
