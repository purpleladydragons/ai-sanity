FROM mcr.microsoft.com/playwright/python:v1.32.1-focal


# Set the working directory in the container
WORKDIR /app

# Copy the application files to the container
COPY . .

# Install any required packages using pip
RUN pip install --no-cache-dir -r requirements.txt

# Run the command to start the application
CMD ["python", "src/main.py"]