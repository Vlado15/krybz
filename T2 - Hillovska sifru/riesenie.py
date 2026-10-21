# 1. determinant matice 3x3
def determinant(a):
    return (
        a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
        - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
        + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0])
    )


# 2. inverzna matica modulo 26
def inverzna_matica(a):
    inverzny_det = pow(determinant(a), -1, 26)
    inverzna = [[0] * 3 for _ in range(3)]

    for i in range(3):
        for j in range(3):
            mensia = [
                [a[r][s] for s in range(3) if s != j]
                for r in range(3) if r != i
            ]
            kofaktor = (-1) ** (i + j) * (
                mensia[0][0] * mensia[1][1] - mensia[0][1] * mensia[1][0]
            )
            inverzna[j][i] = inverzny_det * kofaktor % 26

    return inverzna


# 3. nasobenie matic modulo 26
def nasob_matice(a, b):
    return [
        [sum(a[i][k] * b[k][j] for k in range(3)) % 26 for j in range(3)]
        for i in range(3)
    ]


# 4. vypis matice
def vypis_maticu(a):
    for riadok in a:
        print(*riadok)


# 5. desifrovanie trigramov
def desifruj(sifra, inverzny_kluc):
    text = []
    for i in range(0, len(sifra), 3):
        for r in range(3):
            sucet = sum(
                inverzny_kluc[r][s] * (ord(sifra[i + s]) - ord("A"))
                for s in range(3)
            )
            text.append(chr(ord("A") + sucet % 26))
    return "".join(text)


# 6. main
def main():
    zaciatok = "DRAHYJURAJ"
    sifry = [
        "BALQTGFGYNFUHVLOIVCGPRZJUTHGWOVWCWAJGWN",
        "PCPOVZOJYEJXJLVINLJMIAVAVEUKZLERO",
        "NMUSMRFJGRWSWVKKDJKYTYTNSVMOJW",
    ]
    p = [[ord(zaciatok[3 * s + r]) - ord("A") for s in range(3)] for r in range(3)]
    inverzna_p = inverzna_matica(p)

    print("Matica P:")
    vypis_maticu(p)
    print("Inverzna matica P modulo 26:")
    vypis_maticu(inverzna_p)

    for n, sifra in enumerate(sifry, 1):
        c = [[ord(sifra[3 * s + r]) - ord("A") for s in range(3)] for r in range(3)]
        kluc = nasob_matice(c, inverzna_p)
        inverzny_kluc = inverzna_matica(kluc)

        print(f"\nText {n}\nKluc K = C * P^-1 modulo 26:")
        vypis_maticu(kluc)
        print("Inverzny kluc:")
        vypis_maticu(inverzny_kluc)
        print("Desifrovany text:")
        print(desifruj(sifra, inverzny_kluc))


if __name__ == "__main__":
    main()
