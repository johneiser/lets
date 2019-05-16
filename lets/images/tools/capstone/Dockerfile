FROM python:3

RUN apt-get update && apt-get install -qy libcapstone3
RUN pip install capstone

ADD ./disassemble.py /opt/disassemble.py

WORKDIR /opt