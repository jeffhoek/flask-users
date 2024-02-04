FROM python:3.11

WORKDIR /code

COPY . .

RUN pip3 install -r requirements.txt && pip3 install -e .

#USER 1001

ENTRYPOINT ["python3"]
CMD ["flask_users/app.py"]
