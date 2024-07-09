# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Install any needed packages specified in requirements.txt
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

# Make port 7860 available to the world outside this container
EXPOSE 7860

# Run gunicorn to serve the WSGI app
CMD ["gunicorn", "--bind", "0.0.0.0:80", "wsgi:wsgi"]
