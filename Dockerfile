FROM python:3.6.5
ADD . /code
WORKDIR /code
RUN python setup.py install
CMD python app.py
