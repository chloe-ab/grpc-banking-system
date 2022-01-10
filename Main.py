import grpc
from time import sleep
import json
from Branch import Branch
from Customer import Customer
import argparse
import multiprocessing
from concurrent import futures
import branch_pb2_grpc
import logging

_LOGGER = logging.getLogger(__name__)

def serve_branch(branch):
    branch.create_stubs()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    branch_pb2_grpc.add_BranchServicer_to_server(branch, server)
    port = str(50000 + branch.id)
    server.add_insecure_port("[::]:" + port)
    server.start()
    server.wait_for_termination()

def serve_customer(customer):
    customer.create_stub()
    customer.execute_events()

    output = customer.output()
    output_file = open("output.txt", "a")
    output_file.write(str(output) + "\n")
    output_file.close()

def create_processes(processes):
    customers = []
    customer_processes = []
    branches = []
    branch_ids = []
    branch_processes = []

    for process in processes:
        if process["type"] == "branch":
            branch = Branch(process["id"], process["balance"], branch_ids)
            branches.append(branch)
            branch_ids.append(branch.id)

    for branch in branches:
        branch_process = multiprocessing.Process(target=serve_branch, args=(branch,))
        branch_processes.append(branch_process)
        branch_process.start()

    # Allow time for branch processes to start
    sleep(0.5)

    for process in processes:
        if process["type"] == "customer":
            customer = Customer(process["id"], process["events"])
            customers.append(customer)

    for customer in customers:
        customer_process = multiprocessing.Process(target=serve_customer, args=(customer,))
        customer_processes.append(customer_process)
        customer_process.start()

    for process in customer_processes:
        process.join()

    for process in branch_processes:
        process.terminate()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("json_input")
    args = parser.parse_args()

    try:
        input = json.load(open(args.json_input))
        open("output.txt", "w").close()
        create_processes(input)
    except FileNotFoundError:
        _LOGGER.exception("Input file '" + args.json_input + "' not found.")
    except json.decoder.JSONDecodeError:
        _LOGGER.exception("Error decoding JSON file.")