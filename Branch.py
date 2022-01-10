import grpc
from concurrent import futures
import branch_pb2_grpc
from branch_pb2 import Request, Response

class Branch(branch_pb2_grpc.BranchServicer):
    def __init__(self, id, balance, branches):
        self.id = id
        self.balance = balance
        self.branches = branches
        self.stubList = list()
        self.recv_msg = list()

    def create_stubs(self):
        for branchId in self.branches:
            if branchId != self.id:
                port = str(50000 + branchId)
                channel = grpc.insecure_channel("localhost:" + port)
                self.stubList.append(branch_pb2_grpc.BranchStub(channel))

    def deliver(self, request, context):
        return self.process(request, True)

    def propagate(self, request, context):
        return self.process(request, False)

    def process(self, request, propagate):
        success = True

        if request.money < 0:
            success = False
        elif request.interface == "query":
            pass
        elif request.interface == "deposit":
            self.balance += request.money
            if propagate == True:
                self.propagate_deposit(request)
        elif request.interface == "withdraw":
            if self.balance >= request.money:
                self.balance -= request.money
                if propagate == True:
                    self.propagate_withdraw(request)
            else:
                success = False
        else:
            success = False

        msg = {"interface": request.interface, "success": success}

        if request.interface == "query":
            msg["money"] = request.money

        self.recv_msg.append(msg)

        return Response(interface=request.interface, success=success, money=self.balance)

    def propagate_withdraw(self, request):
        for stub in self.stubList:
            stub.propagate(Request(id=request.id, interface="withdraw", money=request.money))

    def propagate_deposit(self, request):
        for stub in self.stubList:
            stub.propagate(Request(id=request.id, interface="deposit", money=request.money))