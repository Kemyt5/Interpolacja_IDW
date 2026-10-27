import numpy as np
import pandas as pd

#interpolacja danych na siatke
#definiuje wspolrzedne docelowe,znane,warttosci zmierzone oraz potege p
def interpolacja_idw(x_cel, y_cel, x_znane, y_znane, z_znane, p=2):
    #oblicza odleglosc w lini prostej miedzy analizowanym punktem na siatce a wszystkimi znanymi punkatmi
    odleglosc = np.sqrt((x_znane - x_cel) ** 2 + (y_znane - y_cel) ** 2)

    #zabezpieczenie przed bledem dzielenia przez 0
    if np.any(odleglosc < 1e-10):
        #okresla dokladna pozycje indeksu
        indeks = np.argmin(odleglosc)
        #zwraca zmierzona wartosc
        return z_znane.iloc[indeks] if isinstance(z_znane, pd.Series) else z_znane[indeks]

    #wylicza wage dla kazdego punktu pomiarowego
    wagi = 1.0 / (odleglosc ** p)

    #oblicza i zwraca ostateczna wartosc Z ze wzoru na srednia wazona
    wynik = np.sum(wagi * z_znane) / np.sum(wagi)
    return wynik
