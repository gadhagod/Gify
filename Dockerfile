FROM python:3.7
COPY . .
RUN pip3 install -r requirements.txt
CMD ["python", "./main.py"]