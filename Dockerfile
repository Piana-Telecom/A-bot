# Use official Python image based on Debian 12 Bookworm
FROM python:3.12-slim-bookworm

# Set environment variables to automatically accept EULA and run in noninteractive mode
ENV ACCEPT_EULA=Y
ENV DEBIAN_FRONTEND=noninteractive

# Install base dependencies: curl, gnupg, and apt-transport-https
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    apt-transport-https \
    && rm -rf /var/lib/apt/lists/*

# Import the Microsoft public key and add the Microsoft repository with proper signing configuration
RUN curl -sSL https://packages.microsoft.com/keys/microsoft.asc | \
    gpg --dearmor > /usr/share/keyrings/microsoft-archive-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-archive-keyring.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
    > /etc/apt/sources.list.d/mssql-release.list

# Install UnixODBC development files first to avoid potential file conflicts later
RUN apt-get update && apt-get install -y unixodbc-dev && rm -rf /var/lib/apt/lists/*

# Install the Microsoft ODBC driver (msodbcsql18)
RUN apt-get update && apt-get install -y msodbcsql18 && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install Python dependencies (adjust the filename/path as needed)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the /app directory
COPY . /app
WORKDIR /app

# Expose the port your application will run on (adjust as needed)
EXPOSE 8505

# Run your application. For example, this launches a Streamlit app.
CMD ["streamlit", "run", "src/app.py", "--server.port=8505", "--server.address=0.0.0.0"]
