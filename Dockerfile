FROM python:2.7.14-alpine3.4
MAINTAINER Hitesh Sethi "hitesh.28jan@gmail.com"
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["app.py"]
