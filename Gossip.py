#!/usr/bin/env python3
import multiprocessing as mp
import ipaddress
import random
import socket

## Fonctions de protocol Gossip
def Node(ID,IP,V,nodes):

    print(f"Je suis le noeud d'ID {ID} et d'IP : {IP} ")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((str(IP), 0))  # bind to a random port on the node's IP address
    server_socket.listen()

    port = server_socket.getsockname()
    nodes[ID] = (str(IP), port)
    print(f"Node {ID} listening on {IP}:{port}")


    while True:
        # accept connection
        client_socket, client_address = server_socket.accept()

        # read view received
        view = client_socket.recv(1024).decode()

        # print message and the client's address
        print(f"Received message '{view}' from {client_address}")

        # send a response back to other node with his view
        response = f"Node {ID} received message '{view}'"
        client_socket.send(response.encode())

        # close the connection with the client
        client_socket.close()

    
    


    


def Create_Nodes(N,IP):
    ID=100001   
    nodes = {}
    for i in range(0,N):
       
        Process=mp.Process(target=Node,args=(ID,IP[i],[],nodes))
        ID +=1 
        Process.start()
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        for existing_ID, (existing_IP, existing_port) in nodes.items():
            if existing_ID != ID:
                try:
                    client_socket.connect((existing_IP, existing_port))

                    view = f"Hello from node {ID}"
                    client_socket.send(view.encode())
                    response = client_socket.recv(1024).decode()

                    print(f"Received response '{response}' from node {existing_ID}")

                except ConnectionRefusedError:
                    print(f"Could not connect to node {existing_ID}")

                finally:
                    client_socket.close()


        Process.join()



       
def IP_Array(n):
    IP = ipaddress.IPv4Address('127.0.0.1')
    return [IP+i for i in range(n)]

    








