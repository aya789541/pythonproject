import sys
import subprocess
import socket


Hostname=socket.gethostname()
print(Hostname)
# Machine names
with open('Machines.txt','r') as file:
    machine_Names = list(filter(None,file.read().splitlines()))


machine_Names=set(machine_Names)

Machine_Dispo=[]
for Name in machine_Names:
    try:
        result=subprocess.check_output(["ssh", Name, 'exit'], stderr=subprocess.PIPE)
        print("★ ",end="")
        sys.stdout.flush()
        Machine_Dispo.append(Name)
    except:
        print("☆ ",end="")
        sys.stdout.flush()
        continue

while(Hostname in Machine_Dispo):
    print("GG")
    Machine_Dispo.remove(Hostname)

with open('Machine_file', 'w') as file:
    file.write("\n".join(Machine_Dispo))
