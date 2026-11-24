import re
import sys
from pathlib import Path
from time import perf_counter

from cypari2 import Pari


def main():
    zaciatok = perf_counter()

    vstupny_subor = Path(sys.argv[1])
    text = vstupny_subor.read_text(encoding="utf-8")
    hodnoty = dict(re.findall(r"\b([ney])\s*=\s*(\d+)", text))

    cislo_na_delenie = int(hodnoty["n"])
    sifrovacia_mocnina = int(hodnoty["e"])
    zasifrovana_sprava = int(hodnoty["y"])

    pari = Pari()
    rozklad = pari(cislo_na_delenie).factor()
    prve, druhe = map(int, rozklad[0])

    pomocne_cislo = (prve - 1) * (druhe - 1)
    desifrovacia_mocnina = pow(sifrovacia_mocnina, -1, pomocne_cislo)
    povodna_sprava = pow(zasifrovana_sprava, desifrovacia_mocnina, cislo_na_delenie)
    cas_desifrovania = perf_counter() - zaciatok

    priecinok_vystupu = Path(__file__).resolve().parent / "vystup-pokrocily"
    priecinok_vystupu.mkdir(exist_ok=True)
    vystupny_subor = priecinok_vystupu / vstupny_subor.name

    vystupny_subor.write_text(
        f"Verejný kľúč: ({cislo_na_delenie}, {sifrovacia_mocnina})\n"
        f"Súkromný kľúč: ({cislo_na_delenie}, {desifrovacia_mocnina})\n"
        f"Dešifrovaná správa: {povodna_sprava}\n"
        f"Čas dešifrovania: {cas_desifrovania:.9f} s\n",
        encoding="utf-8",
    )

    print(f"Dešifrovaná správa: {povodna_sprava}")
    print(f"Výsledok uložený do {vystupny_subor}")


if __name__ == "__main__":
    main()