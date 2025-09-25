import tkinter as tk
from tkinter import ttk, messagebox, font
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv
import emoji
from PIL import Image, ImageDraw, ImageFont, ImageTk
import win32clipboard

load_dotenv()

DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DATABASE_URL = f"postgresql://postgres:{DB_PASSWORD}@localhost:5432/todolist_db"

Base = declarative_base()

class Tache(Base):
    __tablename__ = 'taches'
    
    id = Column(Integer, primary_key=True)
    description = Column(String(500), nullable=False)
    priorite = Column(String(20), default='Normale')
    terminee = Column(Boolean, default=False)
    date_creation = Column(DateTime, default=datetime.now)

class AppToDo:
    def __init__(self):
        try:
            print(f" tentative de connexion a: {DATABASE_URL}")
            self.engine = create_engine(DATABASE_URL)
            Base.metadata.create_all(self.engine)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            print(f"{self.get_emoji('✅')} Connexion a la base de donnees reussi")
        except Exception as e:
            print(f" erreur de connexion a la base de donnees: {str(e)}")
            input("appuyez sur Entree pour fermer")
            raise SystemExit("Impossible de se connecter à la base de données")
        
        self.fenetre = tk.Tk()
        self.fenetre.title(" Ma liste de taches")
        self.fenetre.geometry("800x600")  # reduced window size
        self.fenetre.configure(bg='#f0f0f0')
        
        self.fenetre.resizable(False, False)
        
        # Configure fonts with emoji support
        self.font_titre = font.Font(family="Helvetica", size=14, weight="bold")
        self.font_normale = font.Font(family="Helvetica", size=11)
        self.font_petite = font.Font(family="Helvetica", size=9)
        self.fenetre.option_add("*Dialog.msg.font", self.font_titre)
        self.fenetre.option_add("*Dialog.button.font", self.font_titre)
        
        self.texte_tache = tk.StringVar()
        self.priorite_selectionnee = tk.StringVar(value="Normale")
        
        self.creer_interface()
        
        self.rafraichir_liste()
    
    def get_emoji(self, emoji_code):
        try:
            return emoji.emojize(emoji_code, language='alias')
        except:
            # Fallback mappings if emoji library fails
            fallback_map = {
                ':check_mark_button:': '✅',
                ':clipboard:': '📋',
                ':check_mark:': '✔️',
                ':wastebasket:': '🗑️',
                ':counterclockwise_arrows_button:': '🔄',
                ':OK_hand:': '👌',
                ':hourglass_not_done:': '⏳',
                ':red_circle:': '🔴',
                ':yellow_circle:': '🟡',
                ':green_circle:': '🟢',
                ':cross_mark:': '❌',
                ':police_car_light:': '🚨',
                ':party_popper:': '🎉',
                ':warning:': '⚠️'
            }
            return fallback_map.get(emoji_code, '')
    
    def emoji_img(self, size, text):
        try:
            font = ImageFont.truetype("seguiemj.ttf", size=int(round(size*72/96, 0))) 
            im = Image.new("RGBA", (size, size), (255, 255, 255, 0))
            draw = ImageDraw.Draw(im)
            draw.text((size/2, size/2), text, embedded_color=True, font=font, anchor="mm")
            return ImageTk.PhotoImage(im)
        except Exception as e:
            print(f"Error creating emoji image: {e}")
            return None
    
    def copy_to_clipboard(self, emoji_text):
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, emoji_text)
            win32clipboard.CloseClipboard()
            print(f"Copied! {emoji_text}")
            messagebox.showinfo("Copié", f"Emoji copié dans le presse-papiers! {emoji_text}")
        except Exception as e:
            print(f"Error copying to clipboard: {e}")
            messagebox.showerror("Erreur", f"Impossible de copier dans le presse-papiers: {str(e)}")
    
    def creer_interface(self):
        self.fenetre.grid_columnconfigure(0, weight=1)
        self.fenetre.grid_rowconfigure(3, weight=1)

        # Title frame
        cadre_titre = tk.Frame(self.fenetre, bg='#2c3e50', height=80)
        cadre_titre.grid(row=0, column=0, sticky='ew')
        cadre_titre.grid_propagate(False)
        titre = tk.Label(cadre_titre, text=" GESTIONNAIRE DE TACHES", 
                        font=self.font_titre, fg='white', bg='#2c3e50')
        titre.pack(expand=True)


        # Add task frame
        cadre_ajout = tk.Frame(self.fenetre, bg='#ecf0f1', relief='raised', bd=2)
        cadre_ajout.grid(row=2, column=0, sticky='ew', padx=10, pady=10)

        label_section = tk.Label(cadre_ajout, text=" Ajouter une nouvelle tâche", 
                                font=self.font_normale, bg='#ecf0f1', fg='#2c3e50')
        label_section.pack(anchor='center', padx=10, pady=(10,5))

        cadre_saisie = tk.Frame(cadre_ajout, bg='#ecf0f1')
        cadre_saisie.pack(fill='x', padx=10, pady=5)

        tk.Label(cadre_saisie, text="Description:", font=self.font_normale, bg='#ecf0f1').pack(anchor='w')

        self.champ_tache = tk.Entry(cadre_saisie, textvariable=self.texte_tache, 
                                      font=self.font_normale, width=50, relief='sunken', bd=2)
        self.champ_tache.pack(fill='x', pady=2)

        cadre_priorite = tk.Frame(cadre_ajout, bg='#ecf0f1')
        cadre_priorite.pack(fill='x', padx=10, pady=5)

        tk.Label(cadre_priorite, text="Priorite:", font=self.font_normale, bg='#ecf0f1').pack(anchor='center')

        priorities = [(" Haute", "Haute"), (" Normale", "Normale"), (" Basse", "Basse")]

        cadre_radio = tk.Frame(cadre_priorite, bg='#ecf0f1')
        cadre_radio.pack(anchor='center')  

        for texte, valeur in priorities:
            rb = tk.Radiobutton(cadre_radio, text=texte, variable=self.priorite_selectionnee,
                                value=valeur, bg='#ecf0f1', font=self.font_normale)
            rb.pack(side='left', padx=10)

        self.bouton_ajouter = tk.Button(cadre_ajout, text=" Ajouter la tache", 
                                         command=self.ajouter_tache,
                                         bg='#27ae60', fg='white', font=self.font_normale,
                                         relief='raised', bd=3, pady=5)
        self.bouton_ajouter.pack(pady=10, anchor='center') 
        # dynamic scrollig
        cadre_liste = tk.Frame(self.fenetre, bg='#ecf0f1', relief='raised', bd=2)
        cadre_liste.grid(row=3, column=0, sticky='nsew', padx=10, pady=(0,10))

        label_liste = tk.Label(cadre_liste, text=f"{self.get_emoji(':clipboard:')} Liste des tâches", 
                               font=self.font_normale, bg='#ecf0f1', fg='#2c3e50')
        label_liste.pack(anchor='w', padx=10, pady=(10,5))

        colonnes = ('ID', 'Description', 'Priorite', 'Statut', 'Date')
        self.arbre_taches = ttk.Treeview(cadre_liste, columns=colonnes, show='headings', height=15)

        self.arbre_taches.heading('ID', text='ID')
        self.arbre_taches.heading('Description', text='Description de la tache')
        self.arbre_taches.heading('Priorite', text='Priorite')
        self.arbre_taches.heading('Statut', text='Statut')
        self.arbre_taches.heading('Date', text='Date craation')

        self.arbre_taches.column('ID', width=50)
        self.arbre_taches.column('Description', width=350)
        self.arbre_taches.column('Priorite', width=100)
        self.arbre_taches.column('Statut', width=120)
        self.arbre_taches.column('Date', width=150)

        scrollbar = tk.Scrollbar(cadre_liste, orient='vertical', command=self.arbre_taches.yview)
        self.arbre_taches.configure(yscrollcommand=scrollbar.set)

        self.arbre_taches.pack(side='left', fill='both', expand=True, padx=(10,0), pady=10)
        scrollbar.pack(side='right', fill='y', pady=10, padx=(0,10))

        self.arbre_taches.tag_configure("high", background="red", foreground="white")
        self.arbre_taches.tag_configure("medium", background="orange", foreground="black")
        self.arbre_taches.tag_configure("low", background="green", foreground="white")

        cadre_boutons = tk.Frame(self.fenetre, bg='#f0f0f0')
        cadre_boutons.grid(row=4, column=0, sticky='ew', padx=10, pady=(0,10))

        self.bouton_terminer = tk.Button(cadre_boutons, text=f"{self.get_emoji(':check_mark:')} Marquer terminée",
                                          command=self.marquer_terminee,
                                          bg='#3498db', fg='white', font=self.font_normale,
                                          relief='raised', bd=2)
        self.bouton_terminer.pack(side='left', padx=5)

        self.bouton_supprimer = tk.Button(cadre_boutons, text=f"{self.get_emoji(':wastebasket:')} Supprimer",
                                           command=self.supprimer_tache,
                                           bg='#e74c3c', fg='white', font=self.font_normale,
                                           relief='raised', bd=2)
        self.bouton_supprimer.pack(side='left', padx=5)

        self.bouton_rafraichir = tk.Button(cadre_boutons, text=f"{self.get_emoji(':counterclockwise_arrows_button:')} Actualiser",
                                            command=self.rafraichir_liste,
                                            bg='#9b59b6', fg='white', font=self.font_normale,
                                            relief='raised', bd=2)
        self.bouton_rafraichir.pack(side='right', padx=5)

        self.fenetre.bind('<Return>', lambda event: self.ajouter_tache())
    
    def ajouter_tache(self):
        description = self.texte_tache.get().strip()
        if not description:
            messagebox.showwarning("Attention", "veuillez saisir une description pour la tache")
            return
        if len(description) > 500:
            messagebox.showwarning("Attention", "La description est trop longue (max 500 caracteres)")
            return
        try:
            nouvelle_tache = Tache(
                description=description,
                priorite=self.priorite_selectionnee.get(),
                terminee=False,
                date_creation=datetime.now()
            )
            
            self.session.add(nouvelle_tache)
            self.session.commit()
            
            self.texte_tache.set("")
            self.priorite_selectionnee.set("Normale")
            
            self.rafraichir_liste()
            
            messagebox.showinfo("Succes", f"{self.get_emoji(':OK_hand:')} tache ajoutee avec succes ")
            
        except Exception as e:
            self.session.rollback()  
            messagebox.showerror("Erreur", f"Impossible d'ajouter la tache:\n{str(e)}")
    
    def rafraichir_liste(self):
        try:
            for item in self.arbre_taches.get_children():
                self.arbre_taches.delete(item)
            
            taches = self.session.query(Tache).order_by(Tache.date_creation.desc()).all()
            
            for tache in taches:
                statut = f"{self.get_emoji('✅')} Terminée" if tache.terminee else f"{self.get_emoji(':hourglass_not_done:')} En cours"
                date_formatee = tache.date_creation.strftime("%d/%m/%Y %H:%M")
                # Définir la couleur en fonction de la priorité
                if tache.priorite == 'Haute':
                    tag = 'high'
                    priorite_emoji = self.get_emoji(':red_circle:')
                elif tache.priorite == 'Normale':
                    tag = 'medium'
                    priorite_emoji = self.get_emoji(':yellow_circle:')
                elif tache.priorite == 'Basse':
                    tag = 'low'
                    priorite_emoji = self.get_emoji(':green_circle:')
                else:
                    tag = ''
                    priorite_emoji = ''

                item_id = self.arbre_taches.insert('', 'end', values=(
                    tache.id,
                    tache.description,
                    f"{priorite_emoji} {tache.priorite}",
                    statut,
                    date_formatee
                ), tags=(tag,))
                
                if tache.terminee:
                    self.arbre_taches.set(item_id, 'Description', f"{self.get_emoji(':cross_mark:')} {tache.description}")
                
                # Appliquer le tag de couleur selon la priorité
                priorite_tag = "low" if tache.priorite == "Basse" else "medium" if tache.priorite == "Normale" else "high"
                self.arbre_taches.item(item_id, tags=(priorite_tag,))
                
        except Exception as e:
            messagebox.showerror("Erreur", f"{self.get_emoji(':police_car_light:')} Impossible de charger les tâches:\n{str(e)}")
    
    def marquer_terminee(self):
        selection = self.arbre_taches.selection()
        if not selection:
            messagebox.showwarning("Attention", f"{self.get_emoji(':police_car_light:')} Veuillez sélectionner une tâche à marquer comme terminée!")
            return
        
        try:
            item = self.arbre_taches.item(selection[0])
            tache_id = item['values'][0]
            
            tache = self.session.query(Tache).filter(Tache.id == tache_id).first()
            
            if tache:
                if tache.terminee:
                    messagebox.showinfo("Information", "Cette tâche est déjà terminée! ")
                    return
                
                tache.terminee = True
                self.session.commit()
                
                self.rafraichir_liste()
                
                messagebox.showinfo("Succès", f"{self.get_emoji(':OK_hand:')} Tâche marquée comme terminée! {self.get_emoji(':party_popper:')}")
            else:
                messagebox.showerror("Erreur", f"{self.get_emoji(':police_car_light:')} Tâche non trouvée!")
                
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Erreur", f"{self.get_emoji(':police_car_light:')} Impossible de marquer la tâche:\n{str(e)}")
    
    def supprimer_tache(self):
        selection = self.arbre_taches.selection()
        if not selection:
            messagebox.showwarning("Attention", f"{self.get_emoji(':police_car_light:')} Veuillez sélectionner une tâche à supprimer!")
            return
        
        reponse = messagebox.askyesno("Confirmation", 
                                     "Êtes-vous sûr de vouloir supprimer cette tâche?\n"
                                     f"Cette action est irréversible! {self.get_emoji(':warning:')}")
        if not reponse:
            return
        
        try:
            item = self.arbre_taches.item(selection[0])
            tache_id = item['values'][0]
            
            tache = self.session.query(Tache).filter(Tache.id == tache_id).first()
            
            if tache:
                self.session.delete(tache)
                self.session.commit()
                
                self.rafraichir_liste()
                
                messagebox.showinfo("Succès", f"{self.get_emoji(':OK_hand:')} tache supprimae avec succas!")
            else:
                messagebox.showerror("Erreur", f"{emoji.emojize(emoji.demojize("☑️"))} tache non trouvae")
                
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Erreur", f"{self.get_emoji(':police_car_light:')} impossible de supprimer la tache:\n{str(e)}")
    
    def fermer_application(self):
        try:
            self.session.close()
            self.fenetre.destroy()
        except:
            pass
    
    def demarrer(self):
        self.fenetre.protocol("WM_DELETE_WINDOW", self.fermer_application)
        print(" Application de gestion de taches demarree")
        self.fenetre.mainloop()

if __name__ == "__main__":
    print("=" * 30)
    print(" Démarrage du todo-list")
    
    try:
        import psycopg2
        print(f"{emoji.emojize(emoji.demojize("👌"))} PostgreSQL fonctionne , c bon !")
    except ImportError:
        print(f"{emoji.emojize(emoji.demojize("🚨"))} PostgreSQL driver manquant!")
        input("Appuyez sur Entrée pour fermer")
        exit(1)
    
    try:
        app = AppToDo()
        app.demarrer()
    except KeyboardInterrupt:
        print("\n Application fermee par le user ")
    except SystemExit:
        pass
    except Exception as e:
        print(f"{emoji.emojize(':police_car_light:', language='alias')} Erreur inattendue lors du demarrage: {e}")
        input("Appuyez sur entree pour fermer")