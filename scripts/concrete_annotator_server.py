#!/usr/bin/env python

from concrete import Communication, LanguageIdentification, UUID, AnnotationMetadata
from concrete.services import Annotator
from concrete.util.concrete_uuid import AnalyticUUIDGeneratorFactory

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TCompactProtocol
from thrift.server import TServer, TNonblockingServer

from valid import model, utils
from pycountry import languages

from glob import glob
import os.path
import re
import time
import uuid
import logging
import pickle
import math
import gzip

class CommunicationHandler():
    def __init__(self, model_path):
        with gzip.open(model_path) as ifd:
            self.classifier = pickle.load(ifd)
    def getDocumentation(self):
        return "Annotation server for VaLID system"
    def annotate(self, communication):
        text = ""
        for section in communication.sectionList:
            if section.kind == "content":
                text += communication.text[section.textSpan.start:section.textSpan.ending]
        scores = {languages.get(iso639_1_code=k).iso639_3_code : math.exp(v) for k, v in self.classifier.classify(text).iteritems()}
        logging.info(str(scores))
        augf = AnalyticUUIDGeneratorFactory(communication)
        aug = augf.create()
        lid = LanguageIdentification(uuid=aug.next(),
                                     languageToProbabilityMap=scores,
                                     metadata=AnnotationMetadata(tool="valid", timestamp=int(time.time()), kBest=len(scores)),
        )
        communication.lidList.append(lid)
        return communication
    
if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", dest="port", type=int, default=9090)
    parser.add_argument("-m", "--model_path", dest="model_path")
    options = parser.parse_args()

    logging.basicConfig(level=logging.ERROR)
    
    handler = CommunicationHandler(options.model_path)
    processor = Annotator.Processor(handler)
    transport = TSocket.TServerSocket(port=options.port)
    ipfactory = TCompactProtocol.TCompactProtocolFactory()
    opfactory = TCompactProtocol.TCompactProtocolFactory()

    server = TNonblockingServer.TNonblockingServer(processor, transport, ipfactory, opfactory)
    logging.info('Starting the server...')
    server.serve()
