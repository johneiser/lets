FROM python:3

RUN apt-get update && apt-get install -y git cmake
RUN git clone https://github.com/keystone-engine/keystone.git /opt/keystone
RUN cd /opt/keystone && mkdir build && cd build && ../make-share.sh && make install
RUN ldconfig

RUN cd /opt/keystone/bindings/python && make install

ADD ./assemble.py /opt/assemble.py

WORKDIR /opt