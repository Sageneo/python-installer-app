import os
import sys
import platform
import subprocess
import tempfile
import shutil
import webbrowser
from urllib.request import urlopen, Request
import re
import json
import gzip
import io
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

class PythonInstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Installateur Python Universel")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Variables
        self.current_version = tk.StringVar(value="Détection...")
        self.available_versions = []
        self.selected_version = tk.StringVar()
        self.system_info = tk.StringVar(value="Détection...")
        self.status = tk.StringVar(value="Prêt")
        
        # Interface
        self.create_widgets()
        
        # Initialisation
        self.detect_system()
        self.detect_python_version()
        self.get_available_versions()
    
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Informations système
        system_frame = ttk.LabelFrame(main_frame, text="Informations système", padding="10")
        system_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(system_frame, text="Système d'exploitation:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(system_frame, textvariable=self.system_info).grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(system_frame, text="Version Python actuelle:").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(system_frame, textvariable=self.current_version).grid(row=1, column=1, sticky=tk.W)
        
        # Versions disponibles
        versions_frame = ttk.LabelFrame(main_frame, text="Versions disponibles", padding="10")
        versions_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Créer un frame pour contenir la listbox et la scrollbar
        list_container = ttk.Frame(versions_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        self.versions_listbox = tk.Listbox(list_container, height=10)
        self.versions_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Barre de défilement
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.versions_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.versions_listbox.config(yscrollcommand=scrollbar.set)
        
        # Actions
        actions_frame = ttk.Frame(main_frame, padding="10")
        actions_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(actions_frame, text="Rafraîchir les versions", command=self.get_available_versions).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Désinstaller Python actuel", command=self.uninstall_python).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Installer la version sélectionnée", command=self.download_and_install).pack(side=tk.LEFT, padx=5)
        
        # Barre de statut
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
        
        ttk.Label(status_frame, textvariable=self.status).pack(side=tk.LEFT)
    
    def detect_system(self):
        system = platform.system()
        arch = platform.architecture()[0]
        processor = platform.processor()
        self.system_info.set(f"{system} ({arch}, {processor})")
        self.system = system
    
    def detect_python_version(self):
        try:
            if self.system == "Windows":
                result = subprocess.run(["python", "--version"], capture_output=True, text=True)
                if result.returncode == 0:
                    self.current_version.set(result.stdout.strip())
                else:
                    self.current_version.set("Non installé")
            else:
                result = subprocess.run(["python3", "--version"], capture_output=True, text=True)
                if result.returncode == 0:
                    self.current_version.set(result.stdout.strip())
                else:
                    self.current_version.set("Non installé")
        except:
            self.current_version.set("Non détecté")
    
    def get_available_versions(self):
        self.status.set("Récupération des versions disponibles...")
        self.versions_listbox.delete(0, tk.END)
        
        try:
            # Méthode alternative utilisant la page des téléchargements
            # Créer une requête avec les en-têtes appropriés
            req = Request("https://www.python.org/downloads/")
            req.add_header('Accept-Encoding', 'gzip')
            req.add_header('User-Agent', 'Mozilla/5.0')
            
            with urlopen(req) as response:
                # Vérifier si la réponse est compressée
                if response.info().get('Content-Encoding') == 'gzip':
                    # Décompresser la réponse
                    buf = io.BytesIO(response.read())
                    response_data = gzip.GzipFile(fileobj=buf).read().decode('utf-8')
                else:
                    # Réponse non compressée
                    response_data = response.read().decode('utf-8')
            
            # Extraire les versions avec une expression régulière
            pattern = r'Python\s+(\d+\.\d+\.\d+)'
            versions = re.findall(pattern, response_data)
            
            # Filtrer et trier les versions
            filtered_versions = []
            for version in versions:
                if not any(x in version for x in ['a', 'b', 'rc']):
                    filtered_versions.append(version)
            
            # Supprimer les doublons et trier
            unique_versions = list(set(filtered_versions))
            unique_versions.sort(key=lambda s: [int(u) for u in s.split('.')], reverse=True)
            
            # Limiter aux 10 dernières versions
            self.available_versions = unique_versions[:10]
            
            # Afficher dans la listbox
            for version in self.available_versions:
                self.versions_listbox.insert(tk.END, f"Python {version}")
            
            self.status.set(f"{len(self.available_versions)} versions disponibles")
        except Exception as e:
            self.status.set(f"Erreur: {str(e)}")
            messagebox.showerror("Erreur", f"Impossible de récupérer les versions: {str(e)}")
    
    def uninstall_python(self):
        if self.system == "Windows":
            self.status.set("Ouverture du panneau de désinstallation...")
            os.system("control appwiz.cpl")
        elif self.system == "Darwin":  # macOS
            msg = """Pour désinstaller Python sur macOS:
1. Supprimez le dossier Python de /Applications
2. Supprimez les liens symboliques dans /usr/local/bin"""
            messagebox.showinfo("Désinstallation sur macOS", msg)
        elif self.system == "Linux":
            msg = """Pour désinstaller Python sur Linux, utilisez le gestionnaire de paquets de votre distribution:
- Ubuntu/Debian: sudo apt-get remove python3
- Fedora: sudo dnf remove python3
- Arch Linux: sudo pacman -R python"""
            messagebox.showinfo("Désinstallation sur Linux", msg)
        else:
            messagebox.showwarning("Non supporté", f"La désinstallation automatique n'est pas supportée pour {self.system}")
    
    def download_and_install(self):
        selected_idx = self.versions_listbox.curselection()
        if not selected_idx:
            messagebox.showwarning("Sélection requise", "Veuillez sélectionner une version à installer")
            return
        
        selected_idx = int(selected_idx[0])  # Convertir en entier
        selected_version = self.available_versions[selected_idx]
        self.status.set(f"Préparation de l'installation de Python {selected_version}...")
        
        if self.system == "Windows":
            if "64" in platform.architecture()[0]:
                url = f"https://www.python.org/ftp/python/{selected_version}/python-{selected_version}-amd64.exe"
            else:
                url = f"https://www.python.org/ftp/python/{selected_version}/python-{selected_version}.exe"
                
            # Télécharger le fichier
            try:
                self.status.set(f"Téléchargement de Python {selected_version}...")
                
                # Créer un dossier temporaire
                temp_dir = tempfile.gettempdir()
                installer_path = os.path.join(temp_dir, f"python-{selected_version}-installer.exe")
                
                # Télécharger le fichier
                with urlopen(url) as response, open(installer_path, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
                
                self.status.set("Téléchargement terminé. Lancement de l'installation...")
                
                # Exécuter l'installateur
                subprocess.Popen([installer_path])
                
                messagebox.showinfo("Installation", f"L'installation de Python {selected_version} a été lancée.")
                
            except Exception as e:
                self.status.set(f"Erreur: {str(e)}")
                messagebox.showerror("Erreur", f"Erreur lors du téléchargement/installation: {str(e)}")
                
        elif self.system == "Darwin":  # macOS
            url = f"https://www.python.org/ftp/python/{selected_version}/python-{selected_version}-macos11.pkg"
            webbrowser.open(url)
            messagebox.showinfo("Téléchargement", f"Le téléchargement de Python {selected_version} pour macOS a été lancé dans votre navigateur.")
            
        elif self.system == "Linux":
            msg = """Pour Linux, utilisez le gestionnaire de paquets de votre distribution:
- Ubuntu/Debian: sudo apt install python3
- Fedora: sudo dnf install python3
- Arch Linux: sudo pacman -S python

Pour les versions spécifiques, consultez le site de votre distribution."""
            messagebox.showinfo("Installation sur Linux", msg)
        else:
            messagebox.showwarning("Non supporté", f"L'installation automatique n'est pas supportée pour {self.system}")

def main():
    root = tk.Tk()
    app = PythonInstallerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
