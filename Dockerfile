FROM python:3.13

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

# Command to start your web server 
CMD ["python", "src/app.py"]  
