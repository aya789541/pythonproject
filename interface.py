import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import filedialog
import subprocess
from PIL import Image, ImageTk


class Application:
    def __init__(self, master):
        self.master = master

        master.title('Affichage des courbes')
        master.geometry("900x600")
        master.resizable(False,False)

        # Load background image
        bg_image = Image.open("background2.jpeg")
        self.bg_image_tk = ImageTk.PhotoImage(bg_image)
        self.bg_label = tk.Label(master, image=self.bg_image_tk)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.frame = tk.Frame(self.bg_label)
        self.frame.pack()

        self.start_button = tk.Button(self.frame, text='Start', command=self.start)
        self.start_button.pack(side='left')

        self.stop_button = tk.Button(self.frame, text='Stop', command=self.stop)
        self.stop_button.pack(side='left')

        self.params_entry = tk.Entry(self.frame)
        self.params_entry.pack(side='left')

        self.run_orch_button = tk.Button(self.frame, text='Run Orchest.py', command=self.run_orchestrateur)
        self.run_orch_button.pack(side='left')

        self.files = ['exemple1.txt', 'exemple2.txt']

        # Create an empty figure and canvas
        self.fig = plt.Figure()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.bg_label)


    def plot_data(self):
        # Lit les données des fichiers
        data1 = []
        data2 = []
        for file in self.files:
            with open(os.path.join(os.getcwd(), file), "r") as f:
                lines = f.readlines()
                # Les fichiers doivent contenir le même nombre de lignes pour pouvoir être tracés ensemble
                if len(lines) != len(data1):
                    data1 = []
                    data2 = []
                for i, line in enumerate(lines):
                    if i >= len(data1):
                        data1.append([])
                        data2.append([])
                    valeurs = line.split()
                    data1[i].append(float(valeurs[0]))
                    data2[i].append(float(valeurs[1]))

        # Trace les courbes
        self.fig.clf()
        self.fig.set_size_inches(7, 5)  # set the figure size
        
        for i in range(len(data1)):
            self.fig.add_subplot(111).plot(data1[i], data2[i])
            self.fig.suptitle('Affichage des courbes')
            self.canvas.draw()

    def start(self):
        # Create the canvas when the "Start" button is clicked
        self.canvas.get_tk_widget().pack(side='bottom', fill='both', expand=True)
        self.plot_data()
        

    def stop(self):
        # Remove the canvas when the "Stop" button is clicked
        self.fig.clf()
        self.canvas.get_tk_widget().pack_forget()
        self.master.update()

    def run_orchestrateur(self):
        # Exécute le programme orchestrateur.py
        #orchestrateur_path = os.path.join(os.getcwd(), "Orchest.py")
        #subprocess.run(["python", orchestrateur_path])
        params = self.params_entry.get()
        cmd = f"python Orchest.py {params}"
        os.system(cmd)


root = tk.Tk()
app = Application(root)
root.mainloop()


