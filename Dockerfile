FROM centos
ENV thrift_version=0.9.1 concrete_version=master MODEL_FILE=models.pkl.gz
MAINTAINER Tom Lippincott <tom.lippincott@gmail.com>
LABEL Description="Base image with Thrift, Concrete, and Python Concrete"

WORKDIR /tmp

RUN yum install -y git libtool make boost zlib-devel gcc-c++ byacc flex python-devel && \
    yum install -y epel-release && \
    yum update -y && \
    yum install -y python-pip patch python-ipython && \
    yum clean all -y

RUN groupadd -r dockeruser && \
    useradd -r -m -g dockeruser dockeruser && \
    chown -R dockeruser:dockeruser /tmp/*

USER dockeruser

RUN git clone https://github.com/apache/thrift.git && \
    cd thrift && \
    git checkout ${thrift_version} && \
    ./bootstrap.sh && \
    ./configure --prefix=/home/dockeruser/local --without-python --without-java && \
    make && \
    make install && \
    export PATH=${PATH}:/home/dockeruser/local/bin && \
    cd lib/py && \
    python setup.py install --user

RUN git clone https://github.com/hltcoe/concrete.git && \
    git clone https://github.com/hltcoe/concrete-python.git && \
    export PATH=${PATH}:/home/dockeruser/local/bin && \
    cd concrete-python && \
    ./build.bash --raw && \
    ./reinstall.bash

COPY . /tmp/VaLID/

USER root

RUN chown -R dockeruser:dockeruser /tmp/*
    
USER dockeruser

RUN cd VaLID && \
    python setup.py install --user
    
EXPOSE 9000

VOLUME /models

CMD python VaLID/scripts/concrete_annotator_server.py -p 9000 -m /models/${MODEL_FILE}