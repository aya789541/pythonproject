import os
import sys
import csv
import socket
import subprocess
import pickle
import time
import select
import threading
from enum import Enum
import numpy as np
import random
import datetime
from math import floor, inf
from os.path import exists
import json

class R_type(Enum):

    AUTHENTIFICATION_REQ = 0
    PULL_REQ = 1
    PULL_RES = 2
    PUSH = 3
    AUTHENTIFICATION_RES = 4


class Request:
    def __init__(self, source, destinataire, req, message):
        self.source=source
        self.destinataire=destinataire
        self.type=R_type(req)
        self.message=message


def List_int(Array):
    for i in range(len(Array)):
        Array[i]=int(Array[i])
    return Array

def time_span(T_r, T_u, T_c):
    Current_time = datetime.datetime.now() # Temps actuelle
    Round_ending_time=Current_time+datetime.timedelta(seconds=T_r) # Temps de fin du round
    Update_ending_time=Round_ending_time+datetime.timedelta(seconds=T_u) # Temps de fin du update
    Connection_ending_time=Update_ending_time+datetime.timedelta(seconds=T_c) # Temps de fin du connection
    
    Current_time_F=Current_time.strftime("%H:%M:%S")
    Round_ending_time_F= Round_ending_time.strftime("%H:%M:%S")
    Update_ending_time_F= Update_ending_time.strftime("%H:%M:%S")
    Connection_ending_time_F= Connection_ending_time.strftime("%H:%M:%S")
    
    return Current_time_F, Round_ending_time_F, Update_ending_time_F, Connection_ending_time_F

def wait_time(Ending_time):
    while(datetime.datetime.now().strftime("%H:%M:%S")!=Ending_time):
        continue


def save_data(N, Nmbr_procs, L1, L2, Rounds, B_percent, T_percent, Views):
    with open("./data/test.json", "w") as f:
        data={"Nodes": N*Nmbr_procs, "Rounds":Rounds, "L1": L1, "L2" : L2, "B%": B_percent, "T%": T_percent, "R_Views":Views}
        f.write(json.dumps(data))
        
def find_indices(list_to_check, item_to_find):
    array = np.array(list_to_check)
    indices = np.where(array == item_to_find)[0]
    return list(indices)

def index_to_ID(Array, id_base):
    return  list(map(lambda x:x+id_base, Array))

def Node_Init_Views(id_base, N, Nmbr_proc, Max_storage, B_percent, T_percent):
    ID_dict={}
    Index=[]
    Machine_Dict=[]
    for i in range(N*Nmbr_proc):
        ID_dict[i+id_base]=[]
        Index.append(0)
    Ids=list(ID_dict.keys())


    # Noeud byzantin
    N_byzantine=floor(N*Nmbr_proc*B_percent)
    ID_byzantine=[]
    while len(ID_byzantine)<N_byzantine:
        for i in range(Nmbr_proc):
            Machine_Ids=check_elemnt_in(Ids[i*N:(i+1)*N], ID_byzantine)
            ID=random.sample(Machine_Ids, 1)[0]
            ID_byzantine.append(ID)
            if len(ID_byzantine)==N_byzantine:
                break

    for Id in ID_byzantine:
        Index[Id-id_base]= inf

    # Noeud de confiance
    N_Trusted=floor(N*Nmbr_proc*T_percent)
    ID_Trusted=random.sample(list(set(ID_byzantine)^set(Ids)), N_Trusted)



    for Id in ID_dict:
        count=0
        while(len(ID_dict[Id])<Max_storage):
            Length_to_fill = Max_storage - len(ID_dict[Id]) # La taille a remplir
            ind = min(Index)
            if count!=0:
                ind+=1
            Indices=find_indices(Index, ind) # Chercher le noeuds qui sont moins présent
            Available_Ids=index_to_ID(Indices, id_base) #ID disponible
            if Id in Available_Ids:
                Available_Ids = list(set(ID_dict[Id]+[Id]) ^ set(Available_Ids)) #ID disponible
            else :
                Available_Ids = list(set(ID_dict[Id]) ^ set(Available_Ids)) #ID disponible
            if not Available_Ids:
                count+=1
            if (Length_to_fill<len(Available_Ids)): # Remplir la vue du noeud
                Ids_To_Add=random.sample(Available_Ids, Length_to_fill) #Choisir Max_storage ID
                if Id not in ID_byzantine:
                    for i in Ids_To_Add:
                        Index[i-id_base]+=1
                ID_dict[Id].extend(Ids_To_Add)
            else:
                if Id not in ID_byzantine:
                    for i in Available_Ids:
                        Index[i-id_base]+=1
                ID_dict[Id].extend(Available_Ids)
    
    for Id in ID_dict:
        if Id in ID_byzantine:
            ID_dict[Id]=["B",ID_dict[Id],ID_byzantine]
        elif Id in ID_Trusted:
            ID_dict[Id]=["T",ID_dict[Id]]
        else:
            ID_dict[Id]=["N",ID_dict[Id]]
    for i in range(Nmbr_proc):
        Aux_dict={}
        for j in range(N):
            Aux_dict[j+id_base]=ID_dict[j+id_base]
        Machine_Dict.append(Aux_dict)
        id_base+=N
    return Machine_Dict, Ids, ID_byzantine

    
def time_stop(N):
    start_time=time.time()
    while (time.time()-start_time)//1<N:
        continue
#                                                    # # #  POLL FUNCTIONS  # # #

def Poll_function(sockets, Machines_Names):
    N=0
    Nmbr_procs=len(Machines_Names)
    # Initialisation
    pollerObject = select.poll()

    # Adding sockets
    for i in sockets:
        pollerObject.register(i, select.POLLIN | select.POLLHUP)

    # Traiter les données
    while(True):
        if N==Nmbr_procs:
            print("Why you stopped me peasant.")
            break
        fdVsEvent = pollerObject.poll(-1)

        for descriptor, Event in fdVsEvent:
            Index=sockets.index(descriptor)
            
            if Index%2==0 and Event==select.POLLHUP:
                N+=1
                print("[+]..",end="")
                break
            
            if Index%2==0 and Event & select.POLLIN:
                Out=os.read(descriptor,4096).decode()
                print(f"[ {Machines_Names[Index//2]}, rang{[Index//2]} ] Out : {Out}",end="")

            elif Index%2==1 and Event & select.POLLIN:
                Err=os.read(descriptor,4096).decode()
                print(f"[ {Machines_Names[Index//2]}, rang{[Index//2]} ] Err : {Err}",end="")

            


                                                    # # # <---  Functions ---> # # #

def check_elemnt_in(Array1, Array2): #remove elements in Array1 if they are in Array2
    Array=[]
    for i in Array1:
        if not i in Array2:
            Array.append(i)
    return Array


def Data_analyser(Data, Ids, ID_byzantine, Rounds, L1):
    IDs_to_check = list(set(Ids) ^ set(ID_byzantine))
    N_normal_nodes = len(IDs_to_check)
    Count_byzantine = 0.0 # Nombre of byzantine nodes in the views
    discovery_percent = 0.75 # Discovery percentage
    time_to_discovery = 0 #Time to discover 75% of non byzantine nodes
                                        ##  Count time to discovery ##
    for Id in IDs_to_check:
        Ids_dicovered=[]
        for k in range(1, Rounds+1):
            Ids_dicovered=list(set(Ids_dicovered) ^ set(check_elemnt_in(Data[k][Id]["View"], ID_byzantine)))
            if (float(len(Ids_dicovered))/N_normal_nodes)>discovery_percent:
                if k>time_to_discovery:
                    time_to_discovery=k
                continue
                                        ## Percentage of Byzantine IDs in the views of correct nodes ##
    for k in range(1, Rounds+1):
        aux=0
        for Id in IDs_to_check:
            ID_N=len(check_elemnt_in(Data[k][Id]["View"], ID_byzantine))
            aux += L1 - ID_N
        if aux>Count_byzantine:
            Count_byzantine=aux
    return Count_byzantine/(len(Ids)*L1), time_to_discovery

def Nodes_info_recv(socket, Nodes_infos):

    # Recieve the len of the dict chiffré
    length=recv_data(socket,4096)
    
    # Recieve the dict
    data=socket.recv(4096)

    while len(data)<length:
        data+=socket.recv(4096)
    Nodes_infos.update(pickle.loads(data))

def Data_recv(socket, Data):
    # Recieve the len of the dict chiffré
    length=recv_data(socket,4096)
    
    # Recieve the dict
    data=socket.recv(4096)
    while len(data)<length:
        data+=socket.recv(4096)
    aux_dict=pickle.loads(data)
    for k in Data:
        Data[k].update(aux_dict[k])

def Listening_socket(IP,Port,N):
    # Créer une socket d'écoute
    Hostname=socket.gethostname() #Nom de la machine
    clientsocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.bind((IP,Port))
    Port=clientsocket.getsockname()[1]
    clientsocket.listen(N)
    return clientsocket

def Gossip_connect(IP_addr,Port):
    conn_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn_socket.connect((IP_addr, int(Port)))
    return conn_socket


def send_data(socket,data):
    data_to_send=pickle.dumps(data)
    Size=len(data_to_send)
    Size_sent=0
    while(Size_sent<Size):
        Size_sent+=socket.send(data_to_send[Size_sent:])


def recv_data(socket,Size):
    data = socket.recv(Size)
    if not data:
        return None
    return pickle.loads(data)

                                                # # # Function d'initialisation # # #
def Net_init():
    # Peer connection mapping
    peer_conn={}

    # se connecter avec le processus pére
    conn_socket=Gossip_connect(sys.argv[1],sys.argv[2])

    # Créer une socket d'écoute
    Hostname=socket.gethostname() #Nom de la machine
    clientsocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.bind((Hostname,0))
    Port=clientsocket.getsockname()[1]

    # Envoyer les infos
    data=[Hostname,Port]
    send_data(conn_socket,data)

    # Recv Nmbr de processus + rang + Mapping des machines
    Nmbr_procs, proc_id, machine_dict=recv_data(conn_socket,4096)


    # Lancer l'écoute
    clientsocket.listen(Nmbr_procs-1)

    time.sleep(1)
    # accepter les connexions des machines de rang supérieur
    for i in range(proc_id,Nmbr_procs-1):
        sock, addr = clientsocket.accept()
        rang = recv_data(sock,1024)
        peer_conn[rang]=[machine_dict[rang][2], sock, machine_dict[rang][0]]

    # se connecter avec les machines de rang inférieur
    for i in range(0,proc_id):
        peer_conn[i]=[machine_dict[i][2], Gossip_connect(machine_dict[i][0], machine_dict[i][1]), machine_dict[i][0]]
        send_data(peer_conn[i][1],proc_id)


    return conn_socket, Nmbr_procs, proc_id, peer_conn




         ############## MAIN ###############

def main():
    # Verifier les arguments
    if len(sys.argv)<17:
        print("Usage : ./Orchest machine_file executable T_launch(s) ID_Base N L1 L2 Rounds T_Round(s) T_update(s) T_connection(s) alpha beta gamma B_percent T_percent")
        exit()
    else:
        Executable=sys.argv[2]
        T_launch=int(sys.argv[3])
        id_base=int(sys.argv[4])
        N=int(sys.argv[5])
        L1=int(sys.argv[6])
        L2=int(sys.argv[7])
        Rounds=int(sys.argv[8])
        T_r=int(sys.argv[9])
        T_u=int(sys.argv[10])
        T_c=int(sys.argv[11])
        B_percent=float(sys.argv[15])
        T_percent=float(sys.argv[16])
        # # Check if we have root privileges
        # if os.geteuid() != 0:
        # # If not, try to elevate privileges
        #     os.seteuid(0)
        #     if os.geteuid() != 0:
        #         # If we still don't have privileges, exit with an error
        #         print("Error: Failed to elevate privileges")
        #         exit(1)

    # Mapping des infos
    machine_dict={}

    # Mapping des sockets
    sockets={}
    # Fd des tubes
    fd_Pipes=[]

    # Machine names
    with open(sys.argv[1],'r') as file:
        machine_Names = list(filter(None,file.read().splitlines()))
    machine_Names_c=machine_Names.copy()
    # Vérifier la disponibilté des machines
    Machine_Dispo=[]
    print("[+]Connecting to machines ",end="")
    for Name in machine_Names:
        try :
            result=subprocess.check_output(["ssh", Name, "exit"], stderr=subprocess.PIPE)
            Machine_Dispo.append(Name)
            print("★ ",end="")
            sys.stdout.flush()
            sys.stderr.flush()
        except :
            print("☆ ",end="")
    # Le nombre des machines disponible
    Nmbr_procs=len(Machine_Dispo)
    
    # Les vues des noeuds
    Nodes_Views, Ids, ID_byzantine=Node_Init_Views(id_base, N, Nmbr_procs, L1, B_percent, T_percent)
    print("Done")
    # heure et minute déxecution
    now_f, Launching_time_f, _, _=time_span(T_launch, 0, 0)
    if Nmbr_procs==0:
        print("\nThere are no machines to run the script on")
        exit(1)
    else :
        print(f"OK\n==> Current time :{now_f}\n==> Launch time :{Launching_time_f}")
    print(f"\n\n\t\t<==  Parameters  ==>\nNode per machine : {N}\nL1 : {L1}\nL2 : {L2}\nRounds : {Rounds}\nRound time span : {T_r}s\nUpdate time span : {T_u}s\nConnection time span : {T_c}s\nByzantine : {B_percent}%\nTrusted: {T_percent}%\n\n")

    # Id bases pour distinguer les noeuds de chaque machine
    ids_bases=[]
    for i in range (Nmbr_procs):
        ids_bases.append(int(id_base)+i*int(N))

    # récuperer le nom de la machine
    Hostname=socket.gethostname()

    # Socket d'écoute
    try:
        serversocket=Listening_socket(Hostname, 0, Nmbr_procs)
    except Exception as e:
        print(e)
        exit(1)
    Port=serversocket.getsockname()[1]


    # Lancer les procs
    for i in range(Nmbr_procs):
        #Liste des arguments
        OutpipeR ,OutpipeW=os.pipe()
        ErrpipeR ,ErrpipeW=os.pipe()
        Args=["ssh",Machine_Dispo[i],"python3","~/Desktop/RAPTEE/"+Executable,Hostname,str(Port),Launching_time_f]+[str(ids_bases[i])]+sys.argv[5:]
        pid=os.fork()
        if pid==0:
            # Redirection des tubes
            os.close(OutpipeR)
            os.dup2(OutpipeW, sys.stdout.fileno())
            os.close(ErrpipeR)
            os.dup2(ErrpipeW, sys.stderr.fileno())
            os.close(OutpipeW)
            os.close(ErrpipeW)
            os.execvp(Args[0],Args)
        elif pid>0:
            os.close(OutpipeW)
            os.close(ErrpipeW)
            fd_Pipes.append(OutpipeR)
            fd_Pipes.append(ErrpipeR)
    # Fonction poll
    t=threading.Thread(target=Poll_function, args=(fd_Pipes, Machine_Dispo,))
    t.start()
    #Node_info threads
    Node_info_threads=[]
    Data_threads=[]
    # dict containing nodes infos
    Nodes_infos={}
    Data={k:{} for k in range(1, Rounds+1)}
    # Accepter les connexions
    for i in range(Nmbr_procs):
        sock_accept,addr=serversocket.accept()
        Acc_infos=recv_data(sock_accept,4096)+[ids_bases[i]] # Hostname, port, Id_base
        rang=Machine_Dispo.index(Acc_infos[0]) # Le rang de la mchine
        if rang in machine_dict :
            machine_Names_c.remove(Acc_infos[0])
            rang=machine_Names_c.index(Acc_infos[0])+1
        machine_dict[rang]=Acc_infos
        sockets[rang]=sock_accept
    # Envoi Nombre de processus + rang + Mapping des machines
    for i in range(Nmbr_procs):
        send_data(sockets[i],[Nmbr_procs,i,machine_dict])
        Node_info_threads.append(threading.Thread(target=Nodes_info_recv, args=(sockets[i], Nodes_infos,)))
        Data_threads.append(threading.Thread(target=Data_recv, args=(sockets[i], Data,)))

    # Sending nodes initial views
    for i in range(Nmbr_procs):
        data_to_send=pickle.dumps(Nodes_Views[i])
        send_data(sockets[i],len(data_to_send))
    time_stop(2) #attendre 2 secondes 
    for i in range(Nmbr_procs):
        send_data(sockets[i], Nodes_Views[i])
        # Lancer les threads pour récupérer les informations des noeuds
        Node_info_threads[i].start()
        
    for i in range(Nmbr_procs):
        Node_info_threads[i].join()
        
    # Envoyer les information à chaque machine
    data_to_send=pickle.dumps(Nodes_infos)
    for i in range(Nmbr_procs):
        send_data(sockets[i], len(data_to_send))
    time_stop(2)
      
    for i in range(Nmbr_procs):
        send_data(sockets[i], Nodes_infos)

    # Lancer les threads pour récupérer Data des échanges
    for i in range(Nmbr_procs):
        Data_threads[i].start()
   
    for i in range(Nmbr_procs):
        Data_threads[i].join()
    
    # Analyse des données
        
    print(Data_analyser(Data, Ids, ID_byzantine, Rounds, L1))

    # Save data
    
    for k in Data:
        for Id in Data[k]:
            Data[k][Id]["View"]=List_int(Data[k][Id]["View"])
            Data[k][Id]["Sample"]=List_int(Data[k][Id]["Sample"])
    save_data(N, Nmbr_procs, L1, L2, Rounds, B_percent, T_percent, Data)

    # attendre la fonction poll
    t.join()

    
if __name__ == '__main__':
    main()
