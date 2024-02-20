#!/usr/bin/env python3

## Fonctions de protocol Brahms

## implémentation en code du pseudo code décrivant le protocol brahms dans le document :
from typing import List, Tuple
import random
import time
import os
import sys
import csv
import socket
import subprocess
import pickle
import time
import select
import threading
from Orchest import R_type, Request
from enum import Enum


#Initialization of parameters
alpha = 0.4
beta = 0.4
gamma = 0.2
#We should always have alpha+beta+gamma=1
p = 0.1
rounds_number = 10 

#Initialisation des noeuds (10 noeuds de confiance sur 100)
nodes_number = 100
nodes_ids = set(range(nodes_number))
trusted_nodes_number = 10
byzantines_nodes_number=5
trusted_nodes = set(random.sample(nodes_ids, trusted_nodes_number))
byzantine_nodes = set(random.sample(nodes_ids - trusted_nodes, byzantines_nodes_number))

print("Identifiants des noeuds de confiance : ", trusted_nodes)
print("Identifiants de tous les noeuds ", nodes_ids)
print("Identifiants des noeuds byzantins ", byzantine_nodes)


#Fonctions utiles 

def push(push_ratio, node_id, node_view, node_address, node_port):
    to_push = int(push_ratio * len(node_view))
    random.shuffle(node_view) #To not have the same list each time

    for i in range(to_push):
        to_send = view[i]
        send_push(to_send, node_address, node_port)


def pull_request(node_i, node_address, node_port):

    # Envoyer la demande pull avec un en-tête de requête
    request_header = "PULL_REQ"
    pull_reply = send_pull_request(request_header, node_address, node_port) 

    return pull_reply

def extract_node_view(request):
    view = request.message
    return view






#classe "Sampler" qui est utilisée pour stocker des échantillons de nœuds. 
# Les échantillons sont utilisés pour sélectionner des nœuds de manière 
# aléatoire dans certaines étapes du protocole.

###########################################################################################

class Sampler:
    #Sampler that chooses a hash function at random and stores the smallest identifier seen so far.

    def __init__(self):
        #Initialise chaque echantillonneur avec une fonction de hachage aleatoire, pas de resultat encore, et pas termine
        self.hash_function = random.randint(0, 1000000)
        self.result = None
        self.done = False

    def __call__(self, identifier):
        # Calcule la valeur de hachage de l'identifiant en utilisant la fonction de hachage de l'echantillonneur
        hash_value = hash(identifier) % self.hash_function
        if self.result is None or hash_value < self.hash_value:
            self.hash_value = hash_value
            self.result = identifier
        return self.result

def l2_sampler(stream, l2):
    #L2 sampler that takes a stream of identifiers and produces a sample list of size l2.
    samplers = [Sampler() for _ in range(l2)]
    for identifier in stream:
        for sampler in samplers:
            identifier = sampler(identifier)
        if all(sampler.done for sampler in samplers):
            break
    return [sampler.result for sampler in samplers]

########################################################################################

def rand(V: Tuple[int], n: int) -> List[int]:
  #return n random choice from V
   return random.sample(list(V), n)


def updateSample(Dynamic_view: List[int], push_messages: List[int], pull_messages: List[int], sample_list: List, alpha: float, beta: float, gamma: float, l1: int) -> List[int]:
   #La fonction "updateSample" met à jour chaque échantillon avec les nouveaux nœuds reçus. 
    random_push_messages = rand(push_messages, int(alpha*l1))
    random_pull_messages = rand(pull_messages, int(beta*l1))
    random_sample_messages = rand(sample_list, int(gamma*l1))

    Dynamic_view = random_push_messages + random_pull_messages + random_sample_messages

    return Dynamic_view

#Gossip protocol est la fonction principale qui implémente le protocole de gossip. 
# Il y a une boucle infinie qui contient plusieurs étapes ( while true)

def __init__(self, V0: List[int], S: List[Sampler], alpha: int, beta: int, gamma: int):
        self.V = tuple(V0)
        self.S = tuple(S)
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.Vpush = []
        self.Vpull = []
        N = V + S  # concatenate tuples V and S




def gossip(self):

        while True:

            self.Vpush = []
            self.Vpull = []


            for i in range (self.alpha*len(self.V)): # envoie des requêtes de type "push" à un nombre limité de nœuds choisis au hasard
                #limited push
                receiver_id= random.choice(self.rand(self.V,1))
                receiver_ip, receiver_port = self.V[receiver_id][1]
                self.push(receiver_id, receiver_ip, receiver_port)

            for i in range (self.beta*len(self.V)): #envoie des requêtes de type "pull" à un autre ensemble de nœuds choisis au hasard
                receiver_id= random.choice(self.rand(self.V,1))
                receiver_ip, receiver_port = self.V[receiver_id][1]
                self.pull_request(receiver_id, receiver_ip, receiver_port)

            #wait(1) Le code attend une seconde avant de poursuivre l'exécution.
            time.sleep(1)

            #Le code récupère ensuite les réponses "push" et "pull" des autres nœuds et 
            # stocke les nœuds reçus dans des listes "Vpush" et "Vpull".

            for (i,id) in self.receive_push_requests(): 
                self.Vpush.append(id)

            for (i, id) in self.receive_pull_requests():
                self.send_pull_reply(i, id)

            for (i, V_i) in self.receive_pull_replies():
                if i in self.sent_pull_requests and len(self.Vpull) == 0:
                    self.Vpull = V_i

            #le code combine les nœuds stockés dans les listes "Vpush" et "Vpull" 
            # avec d'autres nœuds choisis aléatoirement pour créer une nouvelle 
            # liste de nœuds à partir de laquelle les échantillons sont mis à jour.  

            if len(self.Vpush) <= self.alpha*len(self.V) and self.Vpush and self.Vpull:
                V_new = self.rand(self.Vpush, self.alpha*len(self.V)) + self.rand(self.Vpull, self.beta*len(self.V)) + self.rand(self.S, self.gamma*len(self.V))
                self.V = tuple(V_new)
                self.updateSample(self.Vpush + self.Vpull)
            


#fonctions annexes permettant les push et pull request/reply/receive dans le gossip
#entre les nœuds du réseau. Ces fonctions sont définies comme des coquilles vides avec la commande "pass".
# Il  faudra les compléméter une fois qu'on arrivera a connecter plusieurs noeuds entre eux 


def send_push_request(self, i: int, receiver: int):
    # Send push request i to receiver

    pass


def send_pull_request(self, i: int, receiver: int):
    # Send pull request i to receiver

    pass
    
def send_pull_reply(self, i: int, receiver: int):
    # Send pull reply with view V_i to receiver

    pass


def receive_push_requests(self) -> List[Tuple[int, int]]:
    # Receive and parse push requests
    
    return []
    
def receive_pull_requests(self) -> List[Tuple[int, int]]:
    # Receive and parse pull requests
  
    return []

def receive_pull_replies(self) -> List[Tuple[int, List[int]]]:
    # Receive and parse pull replies
   
    return []

V = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
n = 4


result = rand(V, n)
Dynamic_view = []
result1 = updateSample(Dynamic_view,V, V, V, 0.4, 0.4, 0.2, 12)


print(f"Sélection aléatoire de {n} éléments de {V}: {result}")

print(f"La vue dynamique mise à jour est : {result1}")


stream = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
l2 = 3
sample = l2_sampler(stream, l2)
print("La liste S issue de l'échantillonage: ", sample)
V={10000: ['louis', ('10.7.2.102', 33086)], 10001: ['louis', ('10.7.2.102', 53189)], 10002: ['louis', ('10.7.2.102', 46271)], 10003: ['louis', ('10.7.2.102', 57798)], 10004: ['louis', ('10.7.2.102', 39531)], 10005: ['louis', ('10.7.2.102', 56858)], 10006: ['louis', ('10.7.2.102', 60473)], 10007: ['louis', ('10.7.2.102', 42189)], 10008: ['louis', ('10.7.2.102', 36646)], 10009: ['louis', ('10.7.2.102', 38601)], 10010: ['louis', ('10.7.2.102', 34347)], 10011: ['louis', ('10.7.2.102', 48948)], 10012: ['louis', ('10.7.2.102', 56826)], 10013: ['louis', ('10.7.2.102', 48576)], 10014: ['louis', ('10.7.2.102', 43550)], 10015: ['louis', ('10.7.2.102', 53851)]}

receiver_id= random.choice(rand(V,1))
receiver_ip, receiver_port = V[receiver_id][1]

print(f"", {receiver_ip, receiver_id, receiver_port})

# Création d'un message "Request" avec une vue de noeud
view = {1: 'node1', 2: 'node2', 3: 'node3'}
req = Request('nodeA', 'nodeB', 'PULL_REQ', view)

# Extraction de la vue du noeud à partir du message
node_view = extract_node_view(req)

# Affichage de la vue du noeud
print(node_view)