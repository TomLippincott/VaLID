FROM hltcoe/concrete:latest
ENV MODEL_FILE=models.pkl.gz
MAINTAINER Tom Lippincott <tom.lippincott@gmail.com>
LABEL Description="VaLID annotation server"

WORKDIR /tmp

COPY . /tmp/VaLID/

RUN pip install iso639 pycountry --user && \
    cd VaLID && \
    python setup.py install
    
EXPOSE 9090

VOLUME /models

CMD python VaLID/scripts/concrete_annotator_server.py -p 9090 -m /models/${MODEL_FILE}
