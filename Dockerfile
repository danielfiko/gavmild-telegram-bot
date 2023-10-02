FROM python:3.11.5

WORKDIR /code
COPY requirements.txt .
RUN pip install -r requirements.txt --upgrade

COPY app/ .

EXPOSE 5006
CMD ["python", "run.py"]
