import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#import funkcji matematycznej z drugiego pliku
from Obliczenia_problem1 import interpolacja_idw

#definiowanie zmiennych
sciezka_do_pliku = ""

def wybierz_pliku():
    global sciezka_do_pliku
    sciezka = filedialog.askopenfilename(title="Wybierz plik z danymi", filetypes=[("Plik DAT", "*.dat"),("Plik CSV", "*.csv")])
    if sciezka:
        sciezka_do_pliku = sciezka
        text_preview.delete("1.0", tk.END)
        try:
            #wczytanie danych do podgladu okiengowego
            with open(sciezka_do_pliku,"r") as file:
                text_preview.insert(tk.END, file.read())
        except Exception as e:
            text_preview.insert(tk.END, f"Błąd wczytywania pliku: {e}")

def uruchom_interpolacje():
    if not sciezka_do_pliku:
        return

    for widget in right_frame.winfo_children():
        widget.destroy()

    #wczytanie danych do DataFrame
    df = pd.read_csv(sciezka_do_pliku, sep=',', skipinitialspace=True)

    #definiowanie zmiennych
    x = df['Easting']
    y = df['Northing']
    z = df['Elevation']

    rozdzielczosc = int(entry_rozdzielczosc.get())
    p_val = float(entry_p.get())

    #tworzenie siatki dla mapy konturowej
    # np.linspace(minimum,maksimum,liczba_punktow)
    xi = np.linspace(x.min(), x.max(), rozdzielczosc)
    yi = np.linspace(y.min(), y.max(), rozdzielczosc)

    #meshgrid laczy wspolrzedne 1d w dwuwymiarowa siatke (macierze)
    xi,yi = np.meshgrid(xi,yi)

    #przygotowanie pustej macierzy z zerami na wynik(taki sam rozmiar jak xi)
    zi=np.zeros(xi.shape)
    progress['maximum']=rozdzielczosc
    progress['value'] = 0

    #podwojna petla przechodzenie przez kazdy wiersz (i) oraz kazda kolumne (j)
    for i in range(rozdzielczosc):
        for j in range(rozdzielczosc):
            #wyciaganie pojedynczych wspolrzednych docelowych
            x_cel = xi[i, j]
            y_cel = yi[i, j]

            #wyliczenie wysokosci Z dla tego punktu za pomoca zaimportowanej funcji
            zi[i, j] = interpolacja_idw(x_cel, y_cel,x, y, z, p=p_val)

        progress['value'] = i+1
        root.update_idletasks()

    #wizualizacja
    fig, ax = plt.subplots(figsize=(6,5))
    levels = np.arange(25,120,5)

    #wypelnienie mapy kolorami
    cf = ax.contourf(xi, yi, zi, levels=levels, cmap='gist_earth', extend='both')
    fig.colorbar(cf, ax=ax, label='Wysokość (Elevation)')

    #dodanie linii konturowych (izolinii)
    cs = ax.contour(xi, yi, zi, colors="#2E2C2C7D", levels=levels)
    ax.clabel(cs, inline=True, fontsize=10)

    #nalozenie orginalnych puntkow pomiarowych jako czerwone kropki
    ax.grid(True)
    ax.set_title('Mapa konturowa - metoda IDW')
    ax.set_ylabel('Northing')
    ax.set_xlabel('Easting')
    ax.scatter(x, y, c='red', s=20, edgecolors='k', zorder=2)

    #wyswietlenie gotowej mapy w GUI
    canvas = FigureCanvasTkAgg(fig, master=right_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

    #BUDOWA INTERFEJSU GRAFICZNEGO (GUI)

root = tk.Tk()
root.title("Przetwarzanie Geodanych - IDW")
root.geometry("1000x600")

left_frame = tk.Frame(root, width=400, bg="#e0e0e0", padx=10, pady=10)
left_frame.pack(side=tk.LEFT, fill=tk.Y)

right_frame = tk.Frame(root, bg="White")
right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

#przycisk do wyboru pliku z dysku
btn_wybierz = tk.Button(left_frame, text="Wybierz plik z dysku", command=wybierz_pliku, bg="#add8e6", font=("Arial", 10, "bold"))
btn_wybierz.pack(anchor="w", pady=(0,15))

tk.Label(left_frame,text="Podgląd wczytanego pliku - surowego", bg="#e0e0e0",font=("Arial", 10, "bold")).pack(anchor="w")

#Pole tekstowe podgladu pliku razem z scrollbarem
frame_preview = tk.Frame(left_frame)
frame_preview.pack(pady=5)
scrollbar = tk.Scrollbar(frame_preview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
text_preview = tk.Text(frame_preview, height=12, width=45, yscrollcommand=scrollbar.set)
text_preview.pack(side=tk.LEFT, fill=tk.BOTH)
scrollbar.config(command=text_preview.yview)

tk.Label(left_frame, text="Wybieranie parametrów gridingu", bg="#e0e0e0", font=("Arial", 10, "bold")).pack(anchor="w", pady=(15, 5))

# Ramka z ustawieniami parametrów (Rozdzielczość i p)
param_frame = tk.Frame(left_frame, bg="#e0e0e0")
param_frame.pack(anchor="w")

tk.Label(param_frame, text="Rozdzielczość (np. 100):", bg="#e0e0e0").grid(row=0, column=0, sticky="w")
entry_rozdzielczosc = tk.Entry(param_frame, width=10)
entry_rozdzielczosc.insert(0, "100")
entry_rozdzielczosc.grid(row=0, column=1, padx=5, pady=2)

tk.Label(param_frame, text="Potęga IDW (p):", bg="#e0e0e0").grid(row=1, column=0, sticky="w")
entry_p = tk.Entry(param_frame, width=10)
entry_p.insert(0, "2")
entry_p.grid(row=1, column=1, padx=5, pady=2)

# Przycisk wykonujący główną funkcję interpolacji
btn_interpoluj = tk.Button(left_frame, text="Interpoluj", bg="#ffe4b5", font=("Arial", 11, "bold"), width=15, command=uruchom_interpolacje)
btn_interpoluj.pack(anchor="w", pady=(20, 5))

# Pasek postępu
progress = ttk.Progressbar(left_frame, orient="horizontal", length=300, mode="determinate")
progress.pack(anchor="w", pady=10)

if __name__ == "__main__":
    root.mainloop()


