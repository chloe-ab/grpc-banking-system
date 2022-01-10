## Distributed Banking System using gRPC

This project represents a distributed banking system which allows multiple customers to deposit/withdraw money from 
multiple branches of a bank. For simplicity, the assumptions are that there are no concurrent updates on the money in the bank, 
and each customer may only access a single branch. 
Each branch maintains a replica of the money which must be consistent with other branches' replicas. 
A customer may only communicate with a specific branch which shares a unique ID with the customer. 
The replicas stored in each branch must reflect all of the updates made by customers.

gRPC is used to create an interface for the processes to communicate with each other. 

This system contains a branch service, a customer client, a main script which serves as the entry point and spawns branch and customer processes, 
a protocol buffer file, two generated Python files, and an example input file.

* Branch.py: Branch class served as a gRPC server to process customer transactions and propagate them to other branches.
* Customer.py: Customer class with gRPC client branch stub to send transaction requests to its corresponding bank branch.
* branch.proto: Protocol buffer file defining RPC messages and services. 
* branch_pb2.py: Contains request and response classes.
* branch_pb2_grpc.py: Contains client and server classes.
* Input.json: contains a collection of branch and customer processes with transaction events. Format described below.

## Set up
Running the project requires the following:
* Python 3.10.1
* pip 21.2.4

Additionally, the "grpc-tools" 1.43.0 module and its dependencies are required. Install this module and its dependencies using pip. For example, from the Windows command line:
```
python -m pip install grcpio-tools
```
(Re)generate the 2 files: branch_pb2.py and branch_pb2_grpc.py, so that the gRPC code used by the application uses the service defined in the protocol buffer file:
```
$ python -m grpc_tools.protoc -I=[path to source dir] --python_out=[path to destination dir] --grpc_python_out=[path to destination dir] [path to branch.proto]
```
To run the program, a JSON input file is required as a command line argument, which contains information in the following format:

```json
[ // Array of Branch and Customer processes 
  { // Customer process #1 
    "id" : {a unique ID of a customer or a branch},
    "type" : “customer”,
    "events" :  [{"interface":{query | deposit | withdraw}, "money": {an integer value}, “id“: {unique identifier of an event} “dest” {a unique identifier of the branch} } ]
  }
  { … } // Customer process #N 
  { // Branch process #1 
    "id" : {a unique ID of a customer or a branch},
    “type” : “branch”
    “balance” : {replica of the amount of money stored in the branch}
  }
  { … } // Branch process #N 
]
```

Execute the program, which will spawn the server and client processes, from the command line by running:
```
python -m Main Input.json
```

Upon executing, an output.txt file will be created containing each customer's received message output.
