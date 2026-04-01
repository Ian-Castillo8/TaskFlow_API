#use an official python image
FROM python:3.11-slim

#set the working directory in the container
WORKDIR /app

#copy the requirements first
COPY requirements.txt .

#install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

#copy the rest of the application code
COPY . .

#expose the port the app runs on
EXPOSE 5000

#command to run the application
CMD ["python", "run.py"]

