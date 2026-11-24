import re
import sys
from pathlib import Path
from time import perf_counter
from itertools import count
from math import gcd

nazov_suboru = sys.argv[1]


def rozloz_rychlo(cislo):
    for posun in count(1):
        prva_hodnota = 2
        druha_hodnota = 2
        delitel = 1

        while delitel == 1:
            prva_hodnota = (pow(prva_hodnota, 2) + posun) % cislo

            medzivysledok = (pow(druha_hodnota, 2) + posun) % cislo
            druha_hodnota = (pow(medzivysledok, 2) + posun) % cislo

            rozdiel = abs(prva_hodnota - druha_hodnota)
            delitel = gcd(rozdiel, cislo)

        if delitel < cislo:
            return delitel, cislo // delitel


#1. rozklad cisla n na jeho prvočísla
def rozloz_na_prvocisla(cislo):
    delitel = 2

    while delitel * delitel <= cislo:
        if cislo % delitel == 0:
            return delitel, cislo // delitel
        delitel += 1

    raise ValueError("Číslo nemá deliteľa väčšieho ako 1 a menšieho ako ono samo.")


def main():
    zaciatok_celkovo = perf_counter()
    with open(nazov_suboru, encoding="utf-8") as subor:
        riadok = subor.readline()
    hodnoty = dict(re.findall(r"\b([ney])\s*=\s*(\d+)", riadok))

    cislo_na_delenie = hodnoty["n"]
    sifrovacia_mocnina = hodnoty["e"]

    print(f"Verejný kľúč: ({cislo_na_delenie}, {sifrovacia_mocnina})")
    print(f"Súkromný kľúč: ({cislo_na_delenie}, ?)")
    print()

    #1. rozklad cisla n na jeho prvočísla
    cislo_na_delenie = int(hodnoty["n"])
    prve, druhe = rozloz_rychlo(cislo_na_delenie)
    print(f"Rozklad: {cislo_na_delenie} = {prve} × {druhe}")

    #2. odčítanie 1 od prvočísel eulerova funkcia,kolko cisel od 1 do n ma najv.spol.del. 1
    pomocne_cislo = (prve - 1) * (druhe - 1)
    print(f"Pomocné číslo: {pomocne_cislo}")

    #3. výpočet súkromného kľúča
    sifrovacia_mocnina = int(hodnoty["e"])
    desifrovacia_mocnina = pow(sifrovacia_mocnina, -1, pomocne_cislo)
    print(f"Súkromný kľúč: ({cislo_na_delenie}, {desifrovacia_mocnina})")
    print()

    #§4. dešifrovanie správy
    zasifrovana_sprava = int(hodnoty["y"])
    #zs ^ dm % cn
    povodna_sprava = pow(zasifrovana_sprava, desifrovacia_mocnina, cislo_na_delenie)
    cas_desifrovania = perf_counter() - zaciatok_celkovo
    print(f"Dešifrovaná správa: {povodna_sprava}")

    priecinok_vystupu = Path(__file__).resolve().parent / "vystup"
    priecinok_vystupu.mkdir(exist_ok=True)
    vystupny_subor = priecinok_vystupu / Path(nazov_suboru).name

    with vystupny_subor.open("w", encoding="utf-8") as subor:
        subor.write(f"Verejný kľúč: ({cislo_na_delenie}, {sifrovacia_mocnina})\n")
        subor.write(f"Súkromný kľúč: ({cislo_na_delenie}, {desifrovacia_mocnina})\n")
        subor.write(f"Dešifrovaná správa: {povodna_sprava}\n")
        subor.write(f"Čas dešifrovania: {cas_desifrovania:.9f} s\n")

if __name__ == '__main__':
    main()