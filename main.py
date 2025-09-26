import tkinter as tk
from tkinter import ttk, messagebox, font
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont, ImageTk

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
    statut = Column(String(20), default='todo')
    date_creation = Column(DateTime, default=datetime.now)

class AppToDo:
    def __init__(self):
        try:
            print(f" tentative de connexion a: {DATABASE_URL}")
            self.engine = create_engine(DATABASE_URL)
            Base.metadata.create_all(self.engine)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            self.check_and_add_statut_column()
            print("✅ Connexion a la base de donnees reussi")
        except Exception as e:
            print(f" erreur de connexion a la base de donnees: {str(e)}")
            input("appuyez sur Entree pour fermer")
            raise SystemExit("Impossible de se connecter à la base de données")
        
        self.fenetre = tk.Tk()
        self.fenetre.title("📋 Ma liste de taches")
        self.fenetre.geometry("1300x800")
        self.fenetre.configure(bg='#f0f0f0')
        
        self.fenetre.resizable(True, True)
        
        self.font_titre = font.Font(family="Verdana", size=14, weight="bold")
        self.font_normale = font.Font(family="Verdana", size=11, weight="bold")
        self.font_petite = font.Font(family="Verdana", size=10, weight="bold")
        self.fenetre.option_add("*Dialog.msg.font", self.font_titre)
        self.fenetre.option_add("*Dialog.button.font", self.font_titre)
        
        self.texte_tache = tk.StringVar()
        self.priorite_selectionnee = tk.StringVar(value="Normale")
        self.tache_selectionnee = None
        self.arbre_actuel = None
        
        self.creer_interface()
        self.rafraichir_liste()

    def check_and_add_statut_column(self):
        try:
            result = self.session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='taches' AND column_name='statut'"))
            if not result.fetchone():
                self.session.execute(text("ALTER TABLE taches ADD COLUMN statut VARCHAR(20) DEFAULT 'todo'"))
                self.session.execute(text("UPDATE taches SET statut = CASE WHEN terminee = true THEN 'done' ELSE 'todo' END WHERE statut IS NULL"))
                self.session.commit()
                print("📊 Colonne statut ajoutée avec succès")
        except Exception as e:
            print(f"Info: {e}")
    
    def creer_interface(self):
        self.fenetre.grid_columnconfigure(0, weight=1)
        self.fenetre.grid_columnconfigure(1, weight=1)
        self.fenetre.grid_columnconfigure(2, weight=1)
        self.fenetre.grid_rowconfigure(2, weight=1)

        cadre_titre = tk.Frame(self.fenetre, bg='#2c3e50', height=80)
        cadre_titre.grid(row=0, column=0, columnspan=3, sticky='ew')
        cadre_titre.grid_propagate(False)
        titre = tk.Label(cadre_titre, text="📋 GESTIONNAIRE DE TACHES", 
                        font=self.font_titre, fg='white', bg='#2c3e50')
        titre.pack(expand=True)

        cadre_gauche = tk.Frame(self.fenetre, bg="#34badb", relief='raised', bd=2, height=180)
        cadre_gauche.grid(row=1, column=0, sticky='nsew', padx=5, pady=10)
        cadre_gauche.grid_propagate(False)  
        self.charger_image_dans_cadre(cadre_gauche, "image3.jpg", "")
        
        cadre_centre = tk.Frame(self.fenetre, bg="#84cfe2", relief='raised', bd=2)
        cadre_centre.grid(row=1, column=1, sticky='nsew', padx=5, pady=10)
        
        label_section = tk.Label(cadre_centre, text=" AJOUTER UNE TÂCHE", 
                                font=self.font_titre, bg="#9b2093", fg='white',
                                relief='raised', bd=2)
        label_section.pack(fill='x', padx=5, pady=5)

        cadre_saisie = tk.Frame(cadre_centre, bg='#84cfe2')
        cadre_saisie.pack(fill='both', expand=True, padx=15, pady=15)

        tk.Label(cadre_saisie, text="📝 Description:", font=self.font_normale, 
                bg='#84cfe2', fg='#2c3e50').pack(anchor='w', pady=(0,5))

        self.champ_tache = tk.Entry(cadre_saisie, textvariable=self.texte_tache, 
                                  font=self.font_normale, relief='sunken', bd=2,
                                  bg='#84cfe2', fg='#2c3e50')
        self.champ_tache.pack(fill='x', pady=(0,15))

        tk.Label(cadre_saisie, text="⚡ Priorité:", font=self.font_normale, 
                bg='#84cfe2', fg='#2c3e50').pack(anchor='w', pady=(0,8))

        cadre_priorites = tk.Frame(cadre_saisie, bg='#ecf0f1')
        cadre_priorites.pack(fill='x', pady=(0,15))

        priorities = [("🔴 Haute", "Haute", "#dc3545"), 
                     ("🟡 Normale", "Normale", "#fd7e14"), 
                     ("🟢 Basse", "Basse", "#28a745")]

        for texte, valeur, couleur in priorities:
            rb = tk.Radiobutton(cadre_priorites, text=texte, variable=self.priorite_selectionnee,
                               value=valeur, bg='#84cfe2', font=self.font_petite, 
                               fg=couleur, selectcolor='#84cfe2', activeforeground=couleur,
                               anchor='w', activebackground='#84cfe2')
            rb.pack(side='left', padx=0, fill='x', expand=True)

        self.bouton_ajouter = tk.Button(cadre_saisie, text="➕ Ajouter la Tâche", 
                                       command=self.ajouter_tache,
                                       bg='#27ae60', fg='white', font=self.font_normale,
                                       relief='raised', bd=2, cursor='hand2',
                                       activebackground='#229954', activeforeground='white')
        self.bouton_ajouter.pack(fill='x', pady=(5,0), ipady=8)

        cadre_droite = tk.Frame(self.fenetre, bg="#84cfe2", relief='raised', width=280, bd=2, height=180)
        cadre_droite.grid(row=1, column=2, sticky='nsew', padx=5, pady=10)
        cadre_droite.grid_propagate(False) 

        self.charger_image_dans_cadre(cadre_droite, "image4.jpg", "")

        self.creer_colonne_taches("📋 TODO", 0, '#3498db', 'todo')
        self.creer_colonne_taches("⏳ IN PROGRESS", 1, '#f39c12', 'in_progress')
        self.creer_colonne_taches("✅ DONE", 2, '#27ae60', 'done')

        cadre_navigation = tk.Frame(self.fenetre, bg='#f0f0f0')
        cadre_navigation.grid(row=3, column=0, columnspan=3, sticky='ew', padx=5, pady=10)

        cadre_boutons_gauche = tk.Frame(cadre_navigation, bg='#f0f0f0')
        cadre_boutons_gauche.pack(side='left')

        self.bouton_gauche = tk.Button(cadre_boutons_gauche, text="⬅️",
                                        command=self.deplacer_gauche,
                                        bg='#3498db', fg='white', font=self.font_petite,
                                        relief='raised', bd=2)
        self.bouton_gauche.pack(side='left', padx=5)

        self.bouton_droite = tk.Button(cadre_boutons_gauche, text="➡️",
                                        command=self.deplacer_droite,
                                        bg='#3498db', fg='white', font=self.font_petite,
                                        relief='raised', bd=2)
        self.bouton_droite.pack(side='left', padx=5)

        self.bouton_supprimer = tk.Button(cadre_boutons_gauche, text="🗑️Supprimer",
                                           command=self.supprimer_tache,
                                           bg='#e74c3c', fg='white', font=self.font_petite,
                                           relief='raised', bd=2)
        self.bouton_supprimer.pack(side='left', padx=5)

        self.bouton_downgrade_priorite = tk.Button(cadre_boutons_gauche, text="⬇️",
                                                   command=self.diminuer_priorite,
                                                   bg='#f39c12', fg='white', font=self.font_petite,
                                                   relief='raised', bd=2)
        self.bouton_downgrade_priorite.pack(side='left', padx=5)

        self.bouton_upgrade_priorite = tk.Button(cadre_boutons_gauche, text="⬆️",
                                                 command=self.augmenter_priorite,
                                                 bg='#e67e22', fg='white', font=self.font_petite,
                                                 relief='raised', bd=2)
        self.bouton_upgrade_priorite.pack(side='left', padx=5)

        self.bouton_rafraichir = tk.Button(cadre_navigation, text="🔄 Actualiser",
                                            command=self.rafraichir_liste,
                                            bg='#9b59b6', fg='white', font=self.font_petite,
                                            relief='raised', bd=2)
        self.bouton_rafraichir.pack(side='right', padx=5)
        self.fenetre.bind('<Return>', lambda event: self.ajouter_tache())

    def charger_image_dans_cadre(self, parent, nom_image, titre):
        try:
            img = Image.open(nom_image)
            cadre_width = 400 
            cadre_height = 260
            img = img.resize((cadre_width, cadre_height), Image.Resampling.LANCZOS)
            if nom_image == "image3.jpg":
                self.img_gauche = ImageTk.PhotoImage(img)
                image_ref = self.img_gauche
            else:
                self.img_droite = ImageTk.PhotoImage(img)
                image_ref = self.img_droite
            
            label_img = tk.Label(parent, image=image_ref, bg='#ecf0f1', bd=0, highlightthickness=0)
            label_img.pack(fill='both', expand=True, padx=0, pady=0)
        except Exception as e:
            print(f"Erreur lors du chargement de l'image {nom_image}: {e}")
            label_placeholder = tk.Label(parent, 
                                       text=f"Image\n{nom_image}\nnon trouvée", 
                                       bg='#bdc3c7', font=self.font_petite,
                                       justify='center', bd=0, highlightthickness=0)
            label_placeholder.pack(fill='both', expand=True, padx=0, pady=0)

    def creer_colonne_taches(self, titre, colonne, couleur, statut):
        cadre_colonne = tk.Frame(self.fenetre, bg='#ecf0f1', relief='raised', bd=2)
        cadre_colonne.grid(row=2, column=colonne, sticky='nsew', padx=5, pady=(0,10))

        label_titre = tk.Label(cadre_colonne, text=titre, 
                            font=self.font_titre, bg=couleur, fg='white',
                            relief='raised', bd=2)
        label_titre.pack(fill='x', padx=5, pady=5)

        colonnes = ('ID', 'Description', 'Date')
        
        style = ttk.Style()
        style.configure("Custom.Treeview", font=self.font_petite) 
        style.configure("Custom.Treeview.Heading", font=self.font_normale) 
        
        treeview = ttk.Treeview(cadre_colonne, columns=colonnes, show='headings', height=15, style="Custom.Treeview")

        treeview.heading('ID', text='ID')
        treeview.heading('Description', text='Description')  
        treeview.heading('Date', text='Date')

        treeview.column('ID', width=40, stretch=tk.NO)
        treeview.column('Description', width=250, stretch=tk.YES)
        treeview.column('Date', width=100, stretch=tk.NO)

        treeview.tag_configure("high", background="#ffcccb", foreground="#8b0000")
        treeview.tag_configure("medium", background="#ffd580", foreground="#cc5500")
        treeview.tag_configure("low", background="#90ee90", foreground="#006400")

        scrollbar = tk.Scrollbar(cadre_colonne, orient='vertical', command=treeview.yview)
        treeview.configure(yscrollcommand=scrollbar.set)

        treeview.pack(side='left', fill='both', expand=True, padx=(5,0), pady=5)
        scrollbar.pack(side='right', fill='y', pady=5, padx=(0,5))

        treeview.bind('<ButtonRelease-1>', self.on_tache_select)
        treeview.bind('<Motion>', self.show_full_description)
        treeview.bind('<Leave>', self.hide_tooltip_on_leave) 

        if statut == 'todo':
            self.arbre_todo = treeview
        elif statut == 'in_progress':
            self.arbre_progress = treeview
        elif statut == 'done':
            self.arbre_done = treeview
    
    def show_full_description(self, event):
        widget = event.widget
        item_id = widget.identify_row(event.y)
        if hasattr(self, 'current_tooltip') and self.current_tooltip:
            try:
                self.current_tooltip.destroy()
                self.current_tooltip = None
                self.current_tooltip_item = None
            except:
                pass
        if not item_id:
            return
        item = widget.item(item_id)
        task_id = item['values'][0]
        try:
            tache = self.session.query(Tache).filter(Tache.id == task_id).first()
            if tache:
                description = tache.description
                if len(description) > 30: 
                    tooltip = tk.Toplevel(widget)
                    tooltip.wm_overrideredirect(True)
                    tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
                    tooltip.configure(bg="#ffffcc")
                    label = tk.Label(tooltip, text=description, justify='left', 
                                   background="#ffffcc", relief="solid", borderwidth=1,
                                   font=self.font_petite, wraplength=300, padx=8, pady=6)
                    label.pack()
                    self.current_tooltip = tooltip
                    self.current_tooltip_item = item_id
                    def hide_tooltip():
                        try:
                            if hasattr(self, 'current_tooltip') and self.current_tooltip == tooltip:
                                self.current_tooltip.destroy()
                                self.current_tooltip = None
                                self.current_tooltip_item = None
                        except:
                            pass
                    tooltip.after(4000, hide_tooltip)      
        except Exception as e:
            print(f"Error showing full description: {e}")

    def hide_tooltip_on_leave(self, event):
        if hasattr(self, 'current_tooltip') and self.current_tooltip:
            try:
                self.current_tooltip.destroy()
                self.current_tooltip = None
                self.current_tooltip_item = None
            except:
                pass

    def on_tache_select(self, event):
        widget = event.widget
        selection = widget.selection()
        if selection:
            item = widget.item(selection[0])
            self.tache_selectionnee = item['values'][0]
            self.arbre_actuel = widget
            for tree in [self.arbre_todo, self.arbre_progress, self.arbre_done]:
                if tree != widget:
                    tree.selection_remove(tree.selection())
    
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
                statut='todo',
                date_creation=datetime.now()
            )
            self.session.add(nouvelle_tache)
            self.session.commit()
            self.texte_tache.set("")
            self.priorite_selectionnee.set("Normale")
            self.rafraichir_liste()
        except Exception as e:
            self.session.rollback()  
            messagebox.showerror("Erreur", f"Impossible d'ajouter la tâche:\n{str(e)}")
    
    def deplacer_gauche(self):
        if not self.tache_selectionnee:
            messagebox.showwarning("Attention", "Veuillez sélectionner une tâche à déplacer!")
            return
        try:
            tache = self.session.query(Tache).filter(Tache.id == self.tache_selectionnee).first()
            if not tache:
                messagebox.showerror("Erreur", "Tâche non trouvée!")
                return
            if tache.statut == 'in_progress':
                tache.statut = 'todo'
                tache.terminee = False
            elif tache.statut == 'done':
                tache.statut = 'in_progress'
                tache.terminee = False
            else:
                return
            self.session.commit()
            self.rafraichir_liste()
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Erreur", f"Impossible de déplacer la tâche:\n{str(e)}")
    
    def deplacer_droite(self):
        if not self.tache_selectionnee:
            messagebox.showwarning("Attention", "Veuillez sélectionner une tâche à déplacer!")
            return
        try:
            tache = self.session.query(Tache).filter(Tache.id == self.tache_selectionnee).first()
            if not tache:
                messagebox.showerror("Erreur", "Tâche non trouvée!")
                return
            if tache.statut == 'todo':
                tache.statut = 'in_progress'
            elif tache.statut == 'in_progress':
                tache.statut = 'done'
                tache.terminee = True
            else:
                return
            self.session.commit()
            self.rafraichir_liste()
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Erreur", f"Impossible de déplacer la tâche:\n{str(e)}")
    
    def rafraichir_liste(self):
        try:
            for item in self.arbre_todo.get_children():
                self.arbre_todo.delete(item)
            for item in self.arbre_progress.get_children():
                self.arbre_progress.delete(item)
            for item in self.arbre_done.get_children():
                self.arbre_done.delete(item)
            taches = self.session.query(Tache).order_by(Tache.date_creation.desc()).all()
            for tache in taches:
                date_formatee = tache.date_creation.strftime("%d/%m/%Y")
                if tache.priorite == 'Haute':
                    tag = 'high'
                elif tache.priorite == 'Normale':
                    tag = 'medium'
                elif tache.priorite == 'Basse':
                    tag = 'low'
                else:
                    tag = ''
                description_lines = self.split_description(tache.description)
                if tache.statut == 'todo':
                    target_tree = self.arbre_todo
                elif tache.statut == 'in_progress':
                    target_tree = self.arbre_progress
                elif tache.statut == 'done':
                    target_tree = self.arbre_done
                else:
                    if tache.terminee:
                        target_tree = self.arbre_done
                        tache.statut = 'done'
                    else:
                        target_tree = self.arbre_todo
                        tache.statut = 'todo'
                    self.session.commit()
                item_id = target_tree.insert('', 'end', values=(
                    tache.id,
                    description_lines,
                    date_formatee
                ), tags=(tag,))
        except Exception as e:
            messagebox.showerror("Erreur", f"❌ Impossible de charger les tâches:\n{str(e)}")

    def split_description(self, description, max_length=35):
        if len(description) <= max_length:
            return description
        truncated = description[:max_length]
        last_space = truncated.rfind(' ')
        if last_space > max_length * 0.7:  
            return description[:last_space] + "..."
        else:
            return description[:max_length-3] + "..."
    
    def supprimer_tache(self):
        if not self.tache_selectionnee:
            messagebox.showwarning("Attention", "Veuillez sélectionner une tâche à supprimer!")
            return
        reponse = messagebox.askyesno("Confirmation", 
                                     "Êtes-vous sûr de vouloir supprimer cette tâche?\n"
                                     "Cette action est irréversible!")
        if not reponse:
            return
        try:
            tache = self.session.query(Tache).filter(Tache.id == self.tache_selectionnee).first()
            if tache:
                self.session.delete(tache)
                self.session.commit()
                self.tache_selectionnee = None
                self.arbre_actuel = None
                self.rafraichir_liste()
                messagebox.showinfo("Succès", "Tâche supprimée avec succès!")
            else:
                messagebox.showerror("Erreur", "Tâche non trouvée!")
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Erreur", f"Impossible de supprimer la tâche:\n{str(e)}")
    
    def diminuer_priorite(self):
        if not self.tache_selectionnee:
            messagebox.showwarning("Attention", "Veuillez sélectionner une tâche pour modifier sa priorité!")
            return
        try:
            tache = self.session.query(Tache).filter(Tache.id == self.tache_selectionnee).first()
            if not tache:
                messagebox.showerror("Erreur", "Tâche non trouvée!")
                return
            if tache.priorite == 'Haute':
                nouvelle_priorite = 'Normale'
            elif tache.priorite == 'Normale':
                nouvelle_priorite = 'Basse'
            else:
                return
            tache.priorite = nouvelle_priorite
            self.session.commit()
            self.rafraichir_liste()        
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Erreur", f"Impossible de modifier la priorité de la tâche:\n{str(e)}")
    
    def augmenter_priorite(self):
        if not self.tache_selectionnee:
            messagebox.showwarning("Attention", "Veuillez sélectionner une tâche pour modifier sa priorité!")
            return
        try:
            tache = self.session.query(Tache).filter(Tache.id == self.tache_selectionnee).first()
            if not tache:
                messagebox.showerror("Erreur", "Tâche non trouvée!")
                return
            if tache.priorite == 'Basse':
                nouvelle_priorite = 'Normale'
            elif tache.priorite == 'Normale':
                nouvelle_priorite = 'Haute'
            else: 
                return
            tache.priorite = nouvelle_priorite
            self.session.commit()
            self.rafraichir_liste()
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Erreur", f"Impossible de modifier la priorité de la tâche:\n{str(e)}")
    
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
        print("👌 PostgreSQL fonctionne , c bon !")
    except ImportError:
        print("🚨 PostgreSQL driver manquant!")
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
        print(f"🚨 Erreur inattendue lors du demarrage: {e}")
        input("Appuyez sur entree pour fermer")
