FROM python
WORKDIR /app
COPY . .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt
CMD ["python", "bot.py"]

# # Use the official Python image as a base image
# FROM python

# # Set the working directory in the container
# WORKDIR /app

# # Copy the requirements.txt file to the working directory
# COPY requirements.txt ./

# # Install the Python dependencies
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy the Python application files to the working directory
# COPY . .

# # Command to start the Python application
# CMD ["python", "bot.py"]
