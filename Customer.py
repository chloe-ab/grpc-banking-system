import grpc
from time import sleep
import branch_pb2_grpc
from branch_pb2 import Request

class Customer:
    def __init__(self, id, events):
        self.id = id
        self.events = events
        self.recv_msg = list()
        self.stub = None

    def create_stub(self):
        port = str(50000 + self.id)
        channel = grpc.insecure_channel("localhost:" + port)
        self.stub = branch_pb2_grpc.BranchStub(channel)

    def execute_events(self):
        for event in self.events:
            # Allow time for query events
            if event["interface"] == "query":
                sleep(3)

            response = self.stub.deliver(
                Request(id=event["id"], interface=event["interface"], money=event["money"])
            )

            msg = {"interface": response.interface, "success": response.success}

            if response.interface == "query":
                msg["money"] = response.money

            self.recv_msg.append(msg)

    def output(self):
        return {"id": self.id, "recv": self.recv_msg}