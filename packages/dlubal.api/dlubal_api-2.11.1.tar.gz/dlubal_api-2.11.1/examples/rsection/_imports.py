import grpc

import sys
from pathlib import Path
root = str(Path(__file__).parents[2])
sys.path.append(root)
sys.path.append(root+'/rsection')

from rsection.Application_pb2_grpc import ApplicationStub
from rsection.Application_pb2 import EmptyMessage, NewModelRequest
from rsection.Model import Model
from rsection.common.common_pb2 import Empty

from rsection.client import rsection