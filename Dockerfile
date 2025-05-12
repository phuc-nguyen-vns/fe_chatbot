# ENV TARGETPLATFORM=linux/arm64

# Use argument in FROM instruction
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory inside container
WORKDIR /app

# Copy project files into the container
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose Streamlit default port
EXPOSE 8501

# Start Streamlit App (adjust `FE_chatbot/agri.py` if this is the correct path)
CMD ["streamlit", "run", "agri.py", "--server.port=8501", "--server.address=0.0.0.0"]
