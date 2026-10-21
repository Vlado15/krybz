import argparse
import math
from pathlib import Path

# pocty pismen v poradi A az Z
SLOVENSKE_POCTY = [
    228, 27, 61, 100, 160, 26, 4, 40, 163, 36, 93, 60, 81,
    148, 186, 41, 0, 98, 106, 99, 88, 72, 0, 1, 39, 40
]

ANGLICKE_POCTY = [
    374061888, 70195826, 138416451, 169330528, 529117365,
    95422055, 91258980, 216768975, 320410057, 9613410,
    35373464, 183996130, 110504544, 313720540, 326627740,
    90376747, 4550166, 277000841, 294300210, 390965105,
    117295780, 46337161, 79843664, 8369915, 75294515, 4975847
]

# 1. nacitanie suboru
def nacitaj_subor(cesta):
    with open(cesta, "r", encoding="utf-8") as subor:
        povodny_text = subor.read()

    sifra = ""
    for znak in povodny_text:
        if "A" <= znak <= "Z":
            sifra += znak

    return povodny_text, sifra

# 2. vypocet indexu koincidencie
def index_koincidencie(sifra):
    dlzka = len(sifra)
    if dlzka < 2:
        raise ValueError("Sifra musi obsahovat aspon dve pismena.")

    pocty = [0] * 26

    for pismeno in sifra:
        index = ord(pismeno) - ord("A")
        pocty[index] += 1

    rovnake_dvojice = 0
    for pocet in pocty:
        rovnake_dvojice += pocet * (pocet - 1)

    return rovnake_dvojice / (dlzka * (dlzka - 1))

# 3. kaiskeho zhody
def kasiski_zhody(sifra):
    vzdialenosti = []

    for i in range(len(sifra) - 2):
        for j in range(i + 1, len(sifra) - 2):
            if sifra[i:i + 3] == sifra[j:j + 3]:
                vzdialenosti.append(j - i)

    return vzdialenosti

# 4. pocet zhod pre jednotlive dlzky hesla
def spocitaj_zhody(vzdialenosti):
    zhody = {}

    for dlzka in range(15, 26):
        zhody[dlzka] = 0

        for vzdialenost in vzdialenosti:
            if vzdialenost % dlzka == 0:
                zhody[dlzka] += 1

    return zhody

# 6. rozdelenie sifry do skupin
def rozdel_na_skupiny(sifra, dlzka_hesla):
    skupiny = []

    for i in range(dlzka_hesla):
        skupina = sifra[i::dlzka_hesla]
        skupiny.append(skupina)

    return skupiny

# 7. vypocet poctu vyskytu pismen pre jednotlive skupiny
def vyskyt_pismen(skupina):
    pocty = [0] * 26

    for pismeno in skupina:
        index = ord(pismeno) - ord("A")
        pocty[index] += 1

    return pocty

# 8. prevod jazykovych poctov na frekvencie
def jazykove_frekvencie(pocty):
    frekvencie = []
    spolu = sum(pocty) + 26

    for pocet in pocty:
        frekvencie.append((pocet + 1) / spolu)

    return frekvencie

# 9. hladanie najlepsieho posunu skupiny
def najdi_posun(pocty, frekvencie):
    najlepsi_posun = 0
    najlepsie_skore = float("-inf")

    for posun in range(26):
        skore = 0

        for i in range(26):
            pocet = pocty[(i + posun) % 26]
            skore += pocet * math.log(frekvencie[i])

        if skore > najlepsie_skore:
            najlepsie_skore = skore
            najlepsi_posun = posun

    return najlepsi_posun, najlepsie_skore

# 10. zostavenie hesla a jeho celkoveho skore
def zostav_heslo(pocty_skupin, frekvencie):
    heslo = ""
    celkove_skore = 0

    for pocty in pocty_skupin:
        posun, skore = najdi_posun(pocty, frekvencie)
        heslo += chr(ord("A") + posun)
        celkove_skore += skore

    return heslo, celkove_skore


# 11. desifrovanie so zachovanim povodneho formatovania
def desifruj(povodny_text, heslo):
    vysledok = ""
    i = 0

    for znak in povodny_text:
        if "A" <= znak <= "Z":
            posun = ord(heslo[i % len(heslo)]) - ord("A")
            pismeno = (ord(znak) - ord("A") - posun) % 26
            vysledok += chr(ord("A") + pismeno)
            i += 1
        else:
            vysledok += znak

    return vysledok



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("subor")
    args = parser.parse_args()

    # 1. nacitanie sifry a jej ocistenie
    povodny_text, sifra = nacitaj_subor(args.subor)

    # 2. vypocet indexu koincidencie
    index = index_koincidencie(sifra)
    print(f"\nIndex koincidencie: {index}")

    # 3. kaiskeho zhody
    vzdialenosti = kasiski_zhody(sifra)

        # 4. pocet zhod pre jednotlive dlzky hesla
    zhody = spocitaj_zhody(vzdialenosti)
    zoradene = []
    for dlzka, pocet in zhody.items():
        zoradene.append((pocet, dlzka))
    zoradene.sort(reverse=True)
    print("\nPocet zhod:")
    for pocet, dlzka in zoradene:
        print(f"{dlzka}: {pocet}")

    # 5. vyber dlzky hesla
    pocet, dlzka_hesla = zoradene[0]
    print("\nKandidat na dlzku hesla:", dlzka_hesla)

    # 6. rozdelenie sifry do skupin
    skupiny = rozdel_na_skupiny(sifra, dlzka_hesla)

    # 7. vypocet poctu vyskytu pismen pre jednotlive skupiny
    pocty_skupin = []
    for skupina in skupiny:
        pocty = vyskyt_pismen(skupina)
        pocty_skupin.append(pocty)

    # 8. prevod jazykovych poctov na frekvencie
    slovenske_frekvencie = jazykove_frekvencie(SLOVENSKE_POCTY)
    anglicke_frekvencie = jazykove_frekvencie(ANGLICKE_POCTY)

    # 9 a 10. hladanie posunov a zostavenie hesiel
    heslo_sk, skore_sk = zostav_heslo(pocty_skupin, slovenske_frekvencie)
    heslo_en, skore_en = zostav_heslo(pocty_skupin, anglicke_frekvencie)

    print("\nNavrh SK:", heslo_sk, "Skore:", skore_sk)
    print("Navrh EN:", heslo_en, "Skore:", skore_en)
    if skore_sk >= skore_en:
        heslo = heslo_sk
    else:
        heslo = heslo_en
    print("Zvolene heslo:", heslo)

    # 11. desifrovanie
    text = desifruj(povodny_text, heslo)
    print("\nDesifrovany text:")
    print(text)

    # 12. ulozenie vysledku
    priecinok = Path("desifrovanie")
    priecinok.mkdir(exist_ok=True)
    vystup = priecinok / (Path(args.subor).stem + "_dec.txt")
    with open(vystup, "w", encoding="utf-8") as subor:
        subor.write(f"Heslo: {heslo}, dlzka: {len(heslo)}\n\n")
        subor.write(text)


if __name__ == "__main__":
    main()