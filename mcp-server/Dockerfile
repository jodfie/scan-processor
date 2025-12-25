FROM python:3.12-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY server.py .

# Expose port
EXPOSE 8003

# Run the MCP server with streamable HTTP transport
CMD ["python", "server.py"]
