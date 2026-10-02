"""Analyzuje a dešifruje Vigenèrovu šifru nad písmenami A–Z."""

import argparse
import math
from pathlib import Path


# Počty písmen A–Z z dodanej slovenskej frekvenčnej tabuľky (1997 písmen).
SLOVENSKE_POCTY = (
    228, 27, 61, 100, 160, 26, 4, 40, 163, 36, 93, 60, 81,
    148, 186, 41, 0, 98, 106, 99, 88, 72, 0, 1, 39, 40,
)

# Anglické monogramy: https://people.math.sc.edu/Burkardt/datasets/ngrams/english_monograms.txt
ANGLICKE_POCTY = (
    374061888, 70195826, 138416451, 169330528, 529117365, 95422055,
    91258980, 216768975, 320410057, 9613410, 35373464, 183996130,
    110504544, 313720540, 326627740, 90376747, 4550166, 277000841,
    294300210, 390965105, 117295780, 46337161, 79843664, 8369915,
    75294515, 4975847,
)


def je_sifrovane_pismeno(znak: str) -> bool:
    return "A" <= znak <= "Z" or "a" <= znak <= "z"


def priprav_sifru(povodny_text: str) -> str:
    """Odstráni medzery a ponechá iba šifrované písmená A–Z."""
    text_bez_medzier = povodny_text.replace(" ", "")
    return "".join(znak.upper() for znak in text_bez_medzier if je_sifrovane_pismeno(znak))


def vrat_formatovanie(povodny_text: str, otvoreny_text: str) -> str:
    """Dosadí dešifrované písmená a ponechá pôvodné medzery a ostatné znaky."""
    vysledok = []
    pozicia = 0
    for znak in povodny_text:
        if je_sifrovane_pismeno(znak):
            if pozicia >= len(otvoreny_text):
                raise ValueError("Počet dešifrovaných písmen nesedí s pôvodným textom.")
            vysledok.append(otvoreny_text[pozicia])
            pozicia += 1
        else:
            vysledok.append(znak)
    if pozicia != len(otvoreny_text):
        raise ValueError("Počet dešifrovaných písmen nesedí s pôvodným textom.")
    return "".join(vysledok)


def index_koincidencie(text: str) -> float:
    """Pravdepodobnosť, že dve rôzne pozície obsahujú rovnaké písmeno."""
    pocet = [0] * 26
    spolu = 0

    for znak in text.upper():
        if "A" <= znak <= "Z":
            pocet[ord(znak) - ord("A")] += 1
            spolu += 1

    if spolu < 2:
        raise ValueError("Na výpočet sú potrebné aspoň dve písmená A–Z.")

    return sum(n * (n - 1) for n in pocet) / (spolu * (spolu - 1))


def kasiski_zhody(text: str) -> list[tuple[str, int, int, int]]:
    """Vráti opakované trojice: (trojica, prvá pozícia, druhá pozícia, vzdialenosť)."""
    pozicie: dict[str, list[int]] = {}
    zhody = []

    for pozicia in range(len(text) - 2):
        trojica = text[pozicia : pozicia + 3]
        for predosla in pozicie.get(trojica, []):
            zhody.append((trojica, predosla, pozicia, pozicia - predosla))
        pozicie.setdefault(trojica, []).append(pozicia)

    return zhody


def rozdel_na_skupiny(text: str, dlzka_hesla: int) -> list[str]:
    """Skupina i obsahuje znaky šifrované i-tym písmenom hesla."""
    return [text[i::dlzka_hesla] for i in range(dlzka_hesla)]


def frekvencie(text: str) -> list[int]:
    """Vráti počty výskytov písmen A až Z."""
    pocty = [0] * 26
    for znak in text:
        pocty[ord(znak) - ord("A")] += 1
    return pocty


def ohodnot_posuny(skupina: str, jazykove_pocty: tuple[int, ...]) -> list[tuple[str, float]]:
    """Skúsi 26 písmen hesla; vyššia logaritmická vierohodnosť je lepšia."""
    pozorovane = frekvencie(skupina)
    # Pripočítanie 1 zabráni nulovej pravdepodobnosti Q a W v malej vzorke.
    profil = [(pocet + 1) / (sum(jazykove_pocty) + 26) for pocet in jazykove_pocty]
    vysledky = []

    for posun in range(26):
        skore = 0.0
        for pismeno_textu in range(26):
            # Po dešifrovaní sa písmeno šifry na pozícii (i + posun) zmení na i.
            skutocne = pozorovane[(pismeno_textu + posun) % 26]
            skore += skutocne * math.log(profil[pismeno_textu])
        vysledky.append((chr(ord("A") + posun), skore))

    return sorted(vysledky, key=lambda vysledok: vysledok[1], reverse=True)


def odhadni_heslo(text: str, dlzka_hesla: int, jazykove_pocty: tuple[int, ...]) -> tuple[str, float]:
    """Z najlepšieho posunu v každej skupine zostaví heslo a súčet skóre."""
    najlepšie = [ohodnot_posuny(skupina, jazykove_pocty)[0]
                for skupina in rozdel_na_skupiny(text, dlzka_hesla)]
    return "".join(pismeno for pismeno, _ in najlepšie), sum(skore for _, skore in najlepšie)


def priemerny_ik_skupin(text: str, dlzka_hesla: int) -> float:
    """Rozdelí text podľa pozície v hesle a vráti priemerný IK skupín."""
    skupiny = rozdel_na_skupiny(text, dlzka_hesla)
    return sum(index_koincidencie(skupina) for skupina in skupiny) / dlzka_hesla


def kandidati_dlzky(text: str, zhody: list[tuple[str, int, int, int]]) -> list[tuple[int, int, float]]:
    """Pre dĺžky 15–25 spočíta Kasiskiho zhody a priemerný IK skupín."""
    vysledky = []
    for dlzka in range(15, 26):
        if len(text) < 2 * dlzka:
            continue
        pocet_zhod = sum(vzdialenost % dlzka == 0 for _, _, _, vzdialenost in zhody)
        vysledky.append((dlzka, pocet_zhod, priemerny_ik_skupin(text, dlzka)))
    return vysledky


def odhadni_dlzku(kandidati: list[tuple[int, int, float]]) -> int:
    """Vyberie dĺžku s najvyšším IK; Kasiskiho zhody rozhodnú pri zhode."""
    return max(kandidati, key=lambda vysledok: (vysledok[2], vysledok[1]))[0]


def porovnaj_jazyky(text: str, dlzka: int) -> dict[str, tuple[str, float]]:
    """Pre slovenský a anglický profil vráti heslo a skóre celého textu."""
    return {
        "SK": odhadni_heslo(text, dlzka, SLOVENSKE_POCTY),
        "EN": odhadni_heslo(text, dlzka, ANGLICKE_POCTY),
    }


def desifruj(sifra: str, heslo: str) -> str:
    """Od každého písmena šifry odčíta príslušné písmeno hesla modulo 26."""
    if not heslo or any(not "A" <= pismeno <= "Z" for pismeno in heslo):
        raise ValueError("Heslo musí obsahovať iba písmená A–Z.")

    return "".join(
        chr((ord(pismeno) - ord(heslo[i % len(heslo)])) % 26 + ord("A"))
        for i, pismeno in enumerate(sifra)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Analýza a dešifrovanie Vigenèrovej šifry")
    parser.add_argument("subor", type=Path, help="Súbor so zašifrovaným textom")
    parser.add_argument("--dlzka", type=int, help="Použije zvolenú dĺžku hesla")
    parser.add_argument("--heslo", help="Použije zadané heslo namiesto odhadnutého")
    parser.add_argument("--vystup", type=Path, help="Súbor na uloženie dešifrovaného textu")
    args = parser.parse_args()

    if args.dlzka is not None and not 15 <= args.dlzka <= 25:
        parser.error("Dĺžka hesla musí byť od 15 do 25.")
    if args.heslo is not None:
        args.heslo = args.heslo.upper()
        if not 15 <= len(args.heslo) <= 25:
            parser.error("Heslo musí mať dĺžku od 15 do 25.")
        if args.dlzka is not None and len(args.heslo) != args.dlzka:
            parser.error("Dĺžka zadaného hesla sa nezhoduje s --dlzka.")

    try:
        povodny_text = args.subor.read_text(encoding="utf-8")
    except OSError as chyba:
        parser.error(str(chyba))
    sifra = priprav_sifru(povodny_text)

    try:
        ik = index_koincidencie(sifra)
    except ValueError as chyba:
        parser.error(str(chyba))

    print(f"Index koincidencie: {ik:.4f}")

    zhody = kasiski_zhody(sifra)
    print("\nOpakované trojice (pozície sa počítajú od 0):")
    if not zhody:
        print("Žiadne opakované trojice.")
    else:
        for trojica, prva, druha, vzdialenost in zhody:
            print(f"{trojica}: {prva} → {druha}, vzdialenosť {vzdialenost}")

    print("\nMožná dĺžka hesla | Deliteľné vzdialenosti | Priemerný IK skupín")
    kandidati = kandidati_dlzky(sifra, zhody)
    if not kandidati:
        parser.error("Text je príliš krátky na skúšanie dĺžok hesla 15–25.")
    for dlzka, pocet, priemer in kandidati:
        print(f"{dlzka:>19} | {pocet:>21} | {priemer:.4f}")

    odhad_dlzky = odhadni_dlzku(kandidati)
    dlzka = args.dlzka or (len(args.heslo) if args.heslo else odhad_dlzky)
    print(f"\nOdhadnutá dĺžka hesla: {odhad_dlzky}")

    navrhy = porovnaj_jazyky(sifra, dlzka)
    heslo_sk, skore_sk = navrhy["SK"]
    heslo_en, skore_en = navrhy["EN"]
    print(f"Návrh SK: {heslo_sk} (priemerné skóre {skore_sk / len(sifra):.4f})")
    print(f"Návrh EN: {heslo_en} (priemerné skóre {skore_en / len(sifra):.4f})")
    jazyk = max(navrhy, key=lambda nazov: navrhy[nazov][1])
    profil = SLOVENSKE_POCTY if jazyk == "SK" else ANGLICKE_POCTY
    heslo = args.heslo or navrhy[jazyk][0]

    print(f"\nSkupiny a najlepšie posuny ({jazyk}):")
    for i, skupina in enumerate(rozdel_na_skupiny(sifra, dlzka), start=1):
        zoradene = sorted(
            ((chr(ord("A") + j), pocet) for j, pocet in enumerate(frekvencie(skupina)) if pocet),
            key=lambda polozka: (-polozka[1], polozka[0]),
        )
        prehlad = ", ".join(f"{pismeno}:{pocet}" for pismeno, pocet in zoradene)
        posuny = ohodnot_posuny(skupina, profil)
        print(f"{i:>2}. skupina: {skupina}")
        print(f"    Frekvencie: {prehlad}")
        print("    Posuny: " + ", ".join(f"{p}:{skore:.1f}" for p, skore in posuny[:3]))

    try:
        otvoreny_text = desifruj(sifra, heslo)
        zobrazeny_text = vrat_formatovanie(povodny_text, otvoreny_text)
    except ValueError as chyba:
        parser.error(str(chyba))

    print(f"\nZvolené heslo: {heslo}")
    print("\nDešifrovaný text:")
    print(zobrazeny_text)
    if args.vystup is not None:
        try:
            args.vystup.write_text(zobrazeny_text, encoding="utf-8")
        except OSError as chyba:
            parser.error(str(chyba))
        print(f"Uložené do: {args.vystup}")


if __name__ == "__main__":
    main()
