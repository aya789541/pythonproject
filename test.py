import random
from math import floor, inf
import numpy as np
import os
import json

def find_indices(list_to_check, item_to_find):
    array = np.array(list_to_check)
    indices = np.where(array == item_to_find)[0]
    return list(indices)

def index_to_ID(Array, id_base):
    return  list(map(lambda x:x+id_base, Array))

def check_elemnt_in(Array1, Array2): #remove elements in Array1 if they are in Array2
    Array=[]
    for i in Array1:
        if not i in Array2:
            Array.append(i)
    return Array

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

    for id in ID_byzantine:
        Index[id-id_base]= inf

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
    
    for id in ID_dict:
        if id in ID_byzantine:
            ID_dict[id]=["B",ID_dict[id],ID_byzantine]
        elif id in ID_Trusted:
            ID_dict[id]=["T",ID_dict[id]]
        else:
            ID_dict[id]=["N",ID_dict[id]]
    for i in range(Nmbr_proc):
        Aux_dict={}
        for j in range(N):
            Aux_dict[j+id_base]=ID_dict[j+id_base]
        Machine_Dict.append(Aux_dict)
        id_base+=N
    return Machine_Dict, Ids, ID_byzantine

def save_data(N, Nmbr_proc, Max_storage, Rounds, B_percent, T_percent, Views):
    with open("./data/test.json", "w") as f:
        data={"Nodes": N*Nmbr_proc, "Rounds":Rounds, "L1": Max_storage, "L2" : 5, "B%": B_percent, "T%": T_percent, "R_Views":Views}
        f.write(json.dumps(data))



