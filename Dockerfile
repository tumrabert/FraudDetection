FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt ./

# Install all dependencies in one layer
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir \
    streamlit \
    requests \
    jupyter \
    jupyterlab \
    numpy \
    matplotlib \
    seaborn \
    gdown && \
    pip cache purge

# Create necessary directories
RUN mkdir -p /app/data && chmod 777 /app/data && \
    mkdir -p /app/model

# Copy all application code
COPY . .

# Expose all ports
EXPOSE 5000 8501 8888

# Copy startup script
COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]