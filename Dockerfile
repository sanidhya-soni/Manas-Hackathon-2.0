FROM amazon/aws-cli
FROM python:3.10
WORKDIR /app
COPY . .
EXPOSE 5000
RUN pip install -r requirements.txt
CMD ["python3","app.py"]
