import tkinter as tk
import sql


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
selected_value = tk.StringVar()
search_entry = tk.Entry(window, textvariable=selected_value)
search_entry.pack()


suggestion_box = tk.Listbox(window)
suggestion_box.pack()

search_entry.bind('<KeyRelease>', lambda event: show_suggestions())
suggestion_box.bind('<<ListboxSelect>>', select_suggestion)
search_entry.bind('<Return>', store_value_entreprise)



selected_option = tk.StringVar()
selected_option.set("")  # Option sélectionnée par défaut

menu = tk.OptionMenu(window, selected_option, *dates)
menu.pack()

button = tk.Button(window, text='Valider date', command=store_value_date)
button.pack()

def select_prestation():
    cursor.execute("SELECT idPrestation FROM Entreprise, Prestation WHERE nomEntreprise = %s AND dateDebut = %s AND Prestation.idEntreprise = Entreprise.idEntreprise;", (criteres_recherche["nomEntreprise"],criteres_recherche["dateDebut"]))
    prestations = [row[0] for row in cursor.fetchall()]
    if prestations != []:
        criteres_recherche["idPrestation"] = prestations[0]
    print(criteres_recherche["idPrestation"])

button_generator = tk.Button(window, text='Génerer', command=select_prestation)
button_generator.pack()


window.mainloop()




window.mainloop()
