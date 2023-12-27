FROM python:3
WORKDIR /src/
COPY ./src/* .
COPY ./requirements.txt ./requirements.txt
RUN python -m pip install -r ./requirements.txt
EXPOSE 5000
CMD ["python", "loadbalancer.py"]

