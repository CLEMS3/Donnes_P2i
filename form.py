import tkinter as tk
import sql
from PIL import ImageTk, Image
"""
ATTENTION : AVANT DE LANCER LE PROGRAMME :
 -> Se connecter au VPN de l'INSA pour pouvoir acceder à la base de données
 -> Installer la police de caractère "Titillium Web" (dans le dossier du projet)
"""


criteres_recherche = {
    "nomEntreprise": None,
    "dateDebut": None,
    "idPrestation": None
}

connexion_bd = sql.ouvrir_connexion_bd()
cursor = connexion_bd.cursor()
cursor.execute("SELECT nomEntreprise FROM Entreprise;")
entreprises = [row[0] for row in cursor.fetchall()]
cursor.execute("SELECT dateDebut FROM Prestation;")
dates = [row[0] for row in cursor.fetchall()]

def show_suggestions():
    search_text = selected_value.get()
    suggestions = [word for word in entreprises if search_text in word]
    suggestion_box.delete(0, tk.END)
    for suggestion in suggestions:
        suggestion_box.insert(tk.END, suggestion)
    print("Texte entré :", search_text)

def select_suggestion(event):
    # Récupérer l'élément sélectionné dans la liste des suggestions
    selected_item = suggestion_box.get(suggestion_box.curselection())
    # Mettre la valeur sélectionnée dans le champ de recherche
    selected_value.set(selected_item)

def store_value_entreprise(event):
    """
    Stock l'entprise sélectionné et met à jour la liste des dates proposés
    """
    search_text = selected_value.get()
    criteres_recherche["nomEntreprise"] = search_text

    #on met à jour la liste des dates pour n'afficher que celles de l'entreprise sélectionnée
    cursor.execute("SELECT dateDebut FROM Prestation, Entreprise WHERE Prestation.idEntreprise = Entreprise.idEntreprise AND Entreprise.nomEntreprise = %s;", (search_text,))
    dates = [row[0] for row in cursor.fetchall()]

    menu['menu'].delete(0, 'end')
    for option in dates:
        menu['menu'].add_command(label=option, command=tk._setit(selected_option, option))
    selected_option.set("")

    print(dates)

    print("Valeur stockée :", search_text)

def store_value_date():
    """
    Stock la date sélectionnée
    """
    search_text = selected_option.get()
    criteres_recherche["dateDebut"] = search_text
    print("Valeur stockée :", search_text)

window = tk.Tk()

image = Image.open("bg.png")
photo = ImageTk.PhotoImage(image)
label = tk.Label(window, image=photo)

label.pack()
window.title("Génération du rapport")
window.geometry("800x500")
window.iconbitmap("ecrivain.ico")
label = tk.Label(window, text="Génération du rapport", font=("Titillium Web", 20), bg="#504E4B", fg="white")
label.place(x=265, y=20) 

selected_value = tk.StringVar()
search_entry = tk.Entry(window, textvariable=selected_value)
search_entry.place(x=335, y=100)


suggestion_box = tk.Listbox(window)
suggestion_box.place(x=335, y=120)

search_entry.bind('<KeyRelease>', lambda event: show_suggestions())
suggestion_box.bind('<<ListboxSelect>>', select_suggestion)
search_entry.bind('<Return>', store_value_entreprise)



selected_option = tk.StringVar()
selected_option.set("Selectionner")  # Option sélectionnée par défaut

menu = tk.OptionMenu(window, selected_option, *dates)
menu.place(x=342, y=300)

button = tk.Button(window, text='Valider date', command=store_value_date)
button.place(x=360, y=350)

def select_prestation():
    cursor.execute("SELECT idPrestation FROM Entreprise, Prestation WHERE nomEntreprise = %s AND dateDebut = %s AND Prestation.idEntreprise = Entreprise.idEntreprise;", (criteres_recherche["nomEntreprise"],criteres_recherche["dateDebut"]))
    prestations = [row[0] for row in cursor.fetchall()]
    if prestations != []:
        criteres_recherche["idPrestation"] = prestations[0]
    print(criteres_recherche["idPrestation"])

button_generator = tk.Button(window, text='Génerer', command=select_prestation)
button_generator.place(x=370, y=400)


window.mainloop()


