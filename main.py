#!/usr/bin/env python3
import random
import socket
import time
import ipaddress
from Orchest import *
import sys
import threading
import select
import os
import multiprocessing
import datetime
import json
import hashlib
import secrets
from sampler import *
import inspect
import numpy as np




def print_open_fds(print_all=False):
    descriptors = set()
    (frame, filename, line_number, function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
    fds = set(os.listdir('/proc/self/fd/'))
    new_fds = fds - descriptors
    closed_fds = descriptors - fds
    descriptors = fds
    return len(descriptors)
    


class Node:
    def __init__(self, L1, Id, View, L2):

        # Node info
        self.Id = Id   # Node's ID
        self.L1=L1 # View list length
        self.L2=L2 # Sample list length
        self.ip = socket.gethostname()   # Node's IP address
        self.Nu = View  # neighbor list
        self.Su = random.sample(View, L2)  # sample list
        self.PUSH_To=[] # Send push to these nodes
        self.PULL_To=[] # Send pull to these nodes
        self.PUSH_IDS=[] # Pushed IDS
        self.PULL_IDS=[] # Pulled IDS
        self.Public_key=[]
        # Interconnections' info
        self.neighbor_sockets = {}  # Neighbors' IPs and ports
        self.neighbor_acc_sock= {}  # Accepted sockets
        # Listening socket and binding
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Listening socket
        self.sock.bind((self.ip, 0))  # bind socket to node id
        self.port=self.sock.getsockname()[1]
        self.sock.listen(n)  # listen for incoming connections
        #print("Node", self.id, "listening on port", self.port)

    def round_reset(self):
        try : 
            self.PUSH_IDS=[]
            self.PULL_IDS=[]
            self.PULL_To=[]
            self.PUSH_To=[]
            for i in self.neighbor_sockets:
                self.neighbor_sockets[i].close()
            for i in self.neighbor_acc_sock:
                self.neighbor_acc_sock[i].close()
            self.neighbor_sockets = {}
            self.neighbor_acc_sock= {}
        except Exception as e:
            print("Reset : ", e)
            sys.stdout.flush()

    def get_Nu(self):
        return self.Nu
    
    def get_Su(self):
        return self.Su

    def get_Nui(self, i):
        if i < len(self.Nu):
            return self.Nu[i]
        else:
            return None

    def get_Sui(self, i):
        if i < len(self.Su):
            return self.Su[i]
        else:
            return None

    def update_neighbor_list(self, Nu_t):
        # This method updates the sample list of the node with the first L1 elements of the list Su
        self.Nu = Nu_t  # update neighbor list with the first L1 elements

    def update_sample_list(self, Su_t):
        # This method updates the sample list of the node with the first L1 elements of the list Su
        self.Su = Su_t  # update sample list with the first L1 elements


class Trusted(Node):
    def __init__(self,L1, Id, View, L2, Key):
        super().__init__(L1, Id, View, L2)
        self.Private_key=Key

class Byzantine(Node):
    def __init__(self,L1, Id, View, L2, B_ids):
        super().__init__(L1, Id, View, L2)
        self.B_ids=B_ids # ID des autres noeuds byzantin


def Connecting_nodes(nodes, Nodes_infos, n, L1, beta, alpha, End_time):
    node_threads=[]
    thread_event=[]
    for i in range (0,n):
        try:
            thread_event.append(threading.Event())
            node_threads.append(threading.Thread(target=polling_nodes, args=(nodes[i+id_base], thread_event[i],)))
        except Exception as e:
            print(" Conencting threads [1]:", e)
            sys.stdout.flush()
    # Envoi des informations des noeuds
    for i in range(n):
        node_threads[i].start()
    
    for i in range (0,n):
        nodes[i+id_base].PUSH_To=random.sample(nodes[i+id_base].Nu, int(alpha*L1))
        nodes[i+id_base].PULL_To=random.sample(nodes[i+id_base].Nu, int(beta*L1))
        try:
            for Id in set(nodes[i+id_base].PUSH_To + nodes[i+id_base].PULL_To):

                
                neighbor_ip = Nodes_infos[Id][0]

                neighbour_port = Nodes_infos[Id][1]

                nodes[i+id_base].neighbor_sockets[Id] = Gossip_connect(neighbor_ip, neighbour_port)


        except Exception as e:
            print(" Conencting threads [2]:", e)
            sys.stdout.flush()

    wait_time(End_time)
                                                            ### Ending threads ###
    for t_event in thread_event:
        t_event.set()

    for N_thread in node_threads:
        N_thread.join()

    return nodes
            

def encoded(key,rA,rB):

    
    key_bytes = bytes.fromhex(key)

    

    concatenated_values = rA + rB

    hashed = hash(concatenated_values)

    hash_bytes = hashed.to_bytes(8, 'big', signed=True)

    cypher_text = bytearray()

    for i in range (0,len(hash_bytes)):
        cypher_byte = hash_bytes[i]^key_bytes[i]
        
        cypher_text.append(cypher_byte)

    # print(cypher_text)

    return cypher_text

def decode(rA, rB, key,hab):
    key_bytes = bytes.fromhex(key)
    
    concatenated_values = rA + rB
    hashed = hash(concatenated_values)
    hash_bytes = hashed.to_bytes(8, 'big', signed=True)
    # print('Hash bytes calculated decode : ' , hash_bytes)
    
    decypher_text = bytearray()

    for i in range (0,len(hab)):
        decypher_byte = hab[i]^key_bytes[i]
            
        decypher_text.append(decypher_byte)
    
    # print(hash_bytes)
    # print(decypher_text)
    # print(decypher_text)
    if hash_bytes == decypher_text:
        return True
    return False
    # return decypher_text





def Ending_poll(sockets):
    global event 
    global N_ready
    N_ready = 0
    event = threading.Event()
    pollerObject = select.poll()

    # Adding sockets
    [pollerObject.register(sockets[i], select.POLLIN or select.POLLHUP) for i in sockets ]
    while True:
        if event.is_set():
            break
        fdVsEvent = pollerObject.poll(2)

        for descriptor, Event in fdVsEvent:
            if Event==select.POLLHUP:
                continue
            elif Event==select.POLLIN:
                data=recv_data(sockets[descriptor], 4096)
                if data=="END":
                    N_ready+=1
                Event=0
                pollerObject.unregister(sockets[descriptor])

    

def polling_nodes(Node, N_event):
    
    listening_sock=Node.sock
    Sockets={}
    pollerObject = select.poll()



    # Adding sockets
    pollerObject.register(listening_sock, select.POLLIN)
    for sock_N in Node.neighbor_sockets:
        pollerObject.register(Node.neighbor_sockets[sock_N], select.POLLIN or select.POLLHUP)
        Sockets[Node.neighbor_sockets[sock_N].fileno()]=Node.neighbor_sockets[sock_N]

    for sock_N in Node.neighbor_acc_sock:
        pollerObject.register(Node.neighbor_acc_sock[sock_N], select.POLLIN or select.POLLHUP)
        Sockets[Node.neighbor_acc_sock[sock_N].fileno()]=Node.neighbor_acc_sock[sock_N]
    
    
    while True:
        if N_event.is_set():
           break
        fdVsEvent = pollerObject.poll(2)
        for descriptor, Event in fdVsEvent:

            if listening_sock.fileno()==descriptor and Event==select.POLLIN:

                Acc_sock, addr=listening_sock.accept()
                # Adding socket
                Node.neighbor_acc_sock[Acc_sock.fileno()]=Acc_sock

                Sockets[Acc_sock.fileno()]=Acc_sock

                Event=0
            
            elif listening_sock.fileno()!=descriptor and Event==select.POLLIN:
                
                Req=recv_data(Sockets[descriptor],4096)
                if Req==None:
                    continue
                else :
                    if Req.type==R_type.PUSH:

                        Node.PUSH_IDS.append(Req.source)

                        # print("after receiving push")

                    elif Req.type==R_type.PULL_REQ:                         
                        if Node.__class__.__name__=="Byzantine":
                            if len(Node.B_ids)>=L1:
                                Pull_view = random.sample(Node.B_ids, L1)
                            else:
                                Pull_view=Node.B_ids
                                length=L1-len(Pull_view)
                                Pull_view.extend(random.choices(Node.B_ids ,k=length))
                                
                            pull_req = Request(Req.destinataire, Req.source, 2, Pull_view)
                            send_data(Sockets[descriptor], pull_req)  
                        
                        else :
                            pull_req = Request(Req.destinataire, Req.source, 2, Node.Nu)
                            send_data(Sockets[descriptor], pull_req)
                            
                        # Authentification first
                        # rA = secrets.token_bytes(4)

                        
        
                        # to_send_autentification = Request(Req.destinataire, Req.source, 0, rA)

                        # send_data(Sockets[descriptor],to_send_autentification)
                

                    # elif Req.type==R_type.AUTHENTIFICATION_REQ:
                        

                    #     key = "816c7819305c1e1a"
                        
                    #     rA = Req.message

                    #     rB = secrets.token_bytes(4)

                    #     encrypted=encoded(key,rA,rB)

                    #     # print(encrypted)
                    
                    #     to_send_encrypted = [rA,rB,encrypted]
                        
                    #     auth_response_to_send = Request(Req.destinataire, Req.source, 4, to_send_encrypted)

                    #     send_data(Sockets[descriptor],auth_response_to_send)

                    #     # print("PAPAPAPAPAPA")

                    # elif Req.type==R_type.AUTHENTIFICATION_RES:

                    #     encrypted = Req.message

                    #     key = "816c7819305c1e1a"
                        
                    #     can_trust = decode(encrypted[0], encrypted[1], key, encrypted[2])

                        
                        
                    #     # if 1==1  if the node is trusted
                    #     if can_trust==True:
                    #         # print('HOOOOOOOOOOOOOY : Node is trusted')
                    #         # print(can_trust)
                    #         view_to_pull = Request(Req.destinataire, Req.source, 2, Node.Nu)

                            


                    elif Req.type==R_type.PULL_RES:
                        
                        # send_data(Sockets[descriptor],to_send_autentification)
                            
                        Node.PULL_IDS.extend(Req.message)


                        # print("KDA MNAAAAAAAAAAAA")

                    Event=0

                
def Nodes_comunication(node):
    neighbour_samples_push = node.PUSH_To
    neighbour_samples_pull = node.PULL_To

    for Neighbour_Id in neighbour_samples_push:
        sys.stdout.flush()
        to_send_push = Request(node.Id, Neighbour_Id, 3, None)

        try:
            send_data(node.neighbor_sockets[Neighbour_Id],to_send_push)
        except Exception as e:
            print(" Nodes communication [1]:", e)
            sys.stdout.flush()
    
    time_stop(2)
    for Neighbour_Id in neighbour_samples_pull:

        to_send_pull = Request(node.Id, Neighbour_Id, 1, None)

        try:
            send_data(node.neighbor_sockets[Neighbour_Id], to_send_pull)
        except Exception as e:
            print(" Nodes communication [2]:", e)
            sys.stdout.flush()

                    
                    
                    
                    
                    
                    

            


                                                ##### Parameters #####
Launching_time=sys.argv[3]
id_base=int(sys.argv[4])
n=int(sys.argv[5])
L1=int(sys.argv[6])
L2=int(sys.argv[7])
Rounds=int(sys.argv[8])
T_Round=int(sys.argv[9])
update_time=int(sys.argv[10])
connection_time=int(sys.argv[11])
alpha=float(sys.argv[12])
beta=float(sys.argv[13])
gamma=float(sys.argv[14])



                                        ##### Initialisation des connexions #####


Orchest_sock, Nmbr_procs, proc_id, peer_conn=Net_init()

# Recieving dict of Nodes initial views
    # Recieve the len of the encrypted dict
length=recv_data(Orchest_sock,4096)

    # Recieve dict
data=Orchest_sock.recv(4096)
while len(data)<length:
    data+=Orchest_sock.recv(4096)
Nodes_Views=pickle.loads(data)


# Tableau des sockets
Sockets={peer_conn[rang][1].fileno():peer_conn[rang][1] for rang in peer_conn}


# Poll pour finir le programme
t=threading.Thread(target=Ending_poll, args=(Sockets,))
t.start()

nodes={}
Local_Nodes_infos={}
# Creating and initiaizing nodes
for i in range(n):
    Id=i+id_base
    if Nodes_Views[Id][0]=="B":
        nodes[Id]=Byzantine(L1, Id, Nodes_Views[Id][1], L2, Nodes_Views[Id][2])

    elif Nodes_Views[Id][0]=="T":
        nodes[Id]=Trusted(L1, Id, Nodes_Views[Id][1], L2, 0)
        
    else :
        nodes[Id]=Node(L1, Id, Nodes_Views[Id][1], L2)
    Local_Nodes_infos[Id]=[nodes[Id].ip, nodes[Id].port]
    
data_to_send=pickle.dumps(Local_Nodes_infos)
send_data(Orchest_sock, len(data_to_send))
time_stop(1)
send_data(Orchest_sock, Local_Nodes_infos)


# Recieve the len of the encrypted dict
length=recv_data(Orchest_sock,4096)

# Recieve the dict

data=Orchest_sock.recv(4096)
while len(data)<length:
    data+=Orchest_sock.recv(4096)
Nodes_infos=pickle.loads(data)

                                                    ###  Connexion entre noeuds  ###

T_end_connection=datetime.datetime.now()+datetime.timedelta(seconds=connection_time) # Temps de fin du round
nodes=Connecting_nodes(nodes, Nodes_infos, n, L1, beta, alpha, T_end_connection.strftime("%H:%M:%S"))


                                      

# DATA dict
Data={k:{Id:{"View":[],"Sample":[]} for Id in nodes} for k in range(1, Rounds+1)}
Comm_event=[threading.Event() for i in range(n)]

                                                       ### Commencer l'échange au même temps ###
print("[+] Launching...")
sys.stdout.flush()
wait_time(Launching_time)

                                                    ### Commencer les communications ###

for k in range(1, Rounds+1):
    Current_time_F, Round_ending_time_F, Update_ending_time_F, Connection_ending_time_F = time_span(T_Round, update_time, connection_time)
    print(" "*15,"<","="*10,f"  Round :{k}, Nmbr of opened fd : {print_open_fds()} ","="*10,">",f"\n Round beginning : {Current_time_F}, T_comm: {Round_ending_time_F}, T_u : {Update_ending_time_F}, T_c : {Connection_ending_time_F} ")
    sys.stdout.flush()
    node_threads=[]
    nodes_comunication_threads=[]
    for i in range (0,n):
        node_threads.append(threading.Thread(target=polling_nodes, args=(nodes[i+id_base], Comm_event[i],)))
        nodes_comunication_threads.append(threading.Thread(target=Nodes_comunication, args=(nodes[i+id_base],)))

    # Envoi des informations des noeuds   

    for i in range(n):
        if Comm_event[i].is_set():
            Comm_event[i].clear()
        try :
            node_threads[i].start()
        
        except Exception as e:

            print("Communication [1] :", e)
            sys.stdout.flush()



                                                        ###  Échange entre noueds  ###
    for i in range(n):
        nodes_comunication_threads[i].start()

    for i in range(n):
        nodes_comunication_threads[i].join()
        
            
            

                                                            ### Attendre la fin du round ###

    wait_time(Round_ending_time_F)
    
    for t_event in Comm_event:
        t_event.set()

    for N_thread in node_threads:
        N_thread.join()
    


    for Id in nodes:
        if Nodes_Views[Id][0]!="B":
            if (not nodes[Id].PUSH_IDS) or ( len(nodes[Id].PUSH_IDS)>int(alpha*L1) )  :
                Data[k][Id]["View"]=nodes[Id].get_Nu()
                Data[k][Id]["Sample"]=nodes[Id].get_Su()
                nodes[Id].round_reset()
                continue

            try:
                Sample=l2_sampler(nodes[Id].get_Su(), int(gamma*nodes[Id].L1))
            except Exception as e:
                print("Sample : " , e)
                sys.stdout.flush()
            
            try:
                View_update=l2_sampler(nodes[Id].PULL_IDS, int(beta*L1))+l2_sampler(nodes[Id].PUSH_IDS, int(alpha*L1))
            except Exception as e:
                print("PUSH U PULL :", e)
                sys.stdout.flush()
            

            
            try:
                view_up=View_update+Sample
                nodes[Id].update_neighbor_list(View_update+Sample)
                nodes[Id].update_sample_list(l2_sampler( nodes[Id].PULL_IDS + nodes[Id].PUSH_IDS, int(gamma*nodes[Id].L2)) )
                Data[k][Id]["View"]=nodes[Id].get_Nu()
                Data[k][Id]["Sample"]=nodes[Id].get_Su()
            except Exception as e:
                print("Update :", e)
                sys.stdout.flush()
            

                
            try:
                nodes[Id].round_reset()
            except Exception as e:
                print("Reseting [1]:", e)
                sys.stdout.flush()
        else:
            try:
                nodes[Id].round_reset()
            except Exception as e:
                print("Reseting [2]:", e)
                sys.stdout.flush()
                
    #Wait update
    wait_time(Round_ending_time_F)

    if k<Rounds:
        nodes=Connecting_nodes(nodes, Nodes_infos, n, L1, beta, alpha, Connection_ending_time_F)


                                                        ### Sending data to Orchestrator ###
# Envoi des informations des noeuds
data_to_send=pickle.dumps(Data)
send_data(Orchest_sock, len(data_to_send))
time_stop(2)
send_data(Orchest_sock, Data)
                                                        ###  Ending Programme  ###
print(f"End, Opened fd : {print_open_fds()}")
sys.stdout.flush()
N_ready+=1

for i in Sockets:
    send_data(Sockets[i], "END")

# Fin du code
while (N_ready<Nmbr_procs):
    continue

print("END.")
sys.stdout.flush()
event.set()
t.join()




