import argparse
from pathlib import Path

# 2. vytvorenie 256-bajtového kľúča z hesla
def get_key(heslo: str) -> bytes:
    vzor = heslo.encode("ascii")
    kluc = bytearray()

    for i in range(256):
        kluc.append(vzor[i % len(vzor)])

    return bytes(kluc)

# 3. inicializácia stavu RC4
def rc4_init(kluc: bytes) -> list[int]:
    stav = list(range(256))
    j = 0

    for i in range(256):
        j = (j + stav[i] + kluc[i]) % 256
        stav[i], stav[j] = stav[j], stav[i]

    return stav

# 4. vyhenerovanie pseudonáhodného prúdu
def generuj_prud(stav: list[int], dlzka: int) -> bytes:
    stav = stav.copy()
    i = 0
    j = 0
    prud = bytearray()

    for _ in range(dlzka):
        i = (i + 1) % 256
        j = (j + stav[i]) % 256

        stav[i], stav[j] = stav[j], stav[i]

        t = (stav[i] + stav[j]) % 256
        prud.append(stav[t])

    return bytes(prud)

# 5. desifrovanie pomocou XOR
def desifruj(sifra: bytes, prud: bytes) -> bytes:
    text = bytearray()

    for bajt_sifry, bajt_prudu in zip(sifra, prud):
        text.append(bajt_sifry ^ bajt_prudu)

    return bytes(text)

# 6. odhadnutie desifrovaneho textu
def vyzera_ako_text(data: bytes) -> bool:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return False

    if not text:
        return False

    pocet = sum(
        znak.isprintable() or znak in "\t\r\n"
        for znak in text
    )
    return pocet / len(text) >= 0.95

# 7. hladanie hesla
def najdi_hesla(sifra: bytes):
    # Najprv kontrolujeme iba začiatok súboru.
    ukazka = sifra

    # Heslo je 8-ciferné číslo bez úvodnej nuly, zadané ako reťazec.
    for cislo in range(10_000_000, 100_000_000):
        heslo = str(cislo)

        kluc = get_key(heslo)
        stav = rc4_init(kluc)
        prud = generuj_prud(stav, len(ukazka))
        text = desifruj(ukazka, prud)

        if vyzera_ako_text(text):
            # Pri kandidátovi dešifrujeme celý súbor od začiatku.
            stav = rc4_init(kluc)
            prud = generuj_prud(stav, len(sifra))
            cely_text = desifruj(sifra, prud)

            if vyzera_ako_text(cely_text):
                yield heslo, cely_text

        if cislo % 10000 == 0:
            print(f"Skúšam heslo: {heslo}")

# 8. ulozenie kandidatov do suboru
def uloz_subor(cesta: Path, data: bytes) -> None:
    cesta.write_bytes(data)




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("subor", type=Path)
    args = parser.parse_args()

    if not args.subor.exists():
        parser.exit(1, f"Chyba: Súbor '{args.subor}' neexistuje.\n")

    # 1. Načítanie zašifrovaného súboru
    try:
        sifra = args.subor.read_bytes()
    except OSError as chyba:
        parser.exit(1, f"Chyba pri čítaní '{args.subor}': {chyba}\n")

    # 2. Hľadanie hesiel a uloženie kandidátov
    pocet = 0

    for heslo, text in najdi_hesla(sifra):
        vystup = args.subor.with_name(
            f"{args.subor.stem}_heslo_{heslo}_dec.txt"
        )

        try:
            uloz_subor(vystup, text)
        except OSError as chyba:
            parser.exit(1, f"Chyba pri zápise '{vystup}': {chyba}\n")

        pocet += 1
        print(f"\Heslo: {heslo}")
        print(f"Výsledok uložený do: {vystup}")

    print(f"\nHotovo. Počet kandidátov: {pocet}")


if __name__ == "__main__":
    main()
