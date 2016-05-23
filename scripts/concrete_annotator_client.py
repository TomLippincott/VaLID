#!/usr/bin/env python

from concrete import Communication, AnnotationMetadata
from concrete.services import Annotator
from concrete.util.concrete_uuid import AnalyticUUIDGeneratorFactory
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TCompactProtocol
from thrift.server import TServer

import re

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", dest="port", type=int, default=9090)
    parser.add_argument("-H", "--host", dest="host", default="localhost")
    options = parser.parse_args()

    # Make socket
    transport = TSocket.TSocket(options.host, options.port)

    # Buffering is critical. Raw sockets are very slow
    transport = TTransport.TBufferedTransport(transport)

    # Wrap in a protocol
    protocol = TCompactProtocol.TCompactProtocol(transport)

    # Create a client to use the protocol encoder
    client = Annotator.Client(protocol)
    
    # Connect!
    transport.open()

    while True:
        s = raw_input("Write some text > ")
        if re.match(r"^\s*$", s):
            break
        else:
            augf = AnalyticUUIDGeneratorFactory()
            aug = augf.create()
            c = Communication(id="", text=s, uuid=aug.next(), type="tweet", metadata=AnnotationMetadata(timestamp=0, tool="stdin"), lidList=[])

            new_c = client.annotate(c)
            print new_c
