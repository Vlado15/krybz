# Ako riešime Vigenèrovu šifru

Tento návod patrí ku skriptu [`riesenie.py`](riesenie.py). Vysvetľuje postup v poradí, v akom sa vykoná pri spustení programu. Pri každej funkcii uvádza, čo dostane, čo vráti a prečo ju používame.

## Začni tu: čo mám programu zadať?

Keď stojíš v koreňovom priečinku projektu, zadaj do terminálu:

```bash
python3 "T1 - Viegenerovská šifra/riesenie.py" "T1 - Viegenerovská šifra/text1_enc.txt"
```

V tomto príkaze sú **dve cesty**:

| Časť príkazu | Význam |
| --- | --- |
| `python3` | Spustí Python. |
| `.../riesenie.py` | Skript, ktorý vykoná riešenie. |
| `.../text1_enc.txt` | **Jediný povinný vstup, ktorý zadávaš ty:** súbor so šifrou. |

Heslo ani jazyk nezadávaš. Skript ich odhaduje z obsahu súboru. Rovnaký príkaz môžeš použiť s `text2_enc.txt`, `text3_enc.txt` alebo `text4_enc.txt`. Na konci uvidíš heslo a dešifrovaný text. Súbor s výsledkom sa vytvorí iba vtedy, keď pridáš `--vystup` (príklad je v časti 10).

### Argument príkazu nie je to isté ako parameter funkcie

Do terminálu zadávaš cestu k súboru. Python ju uloží do `args.subor`. Potom program obsah súboru načíta a vypočítané hodnoty si **sám posúva medzi funkciami**. Napríklad:

```python
ik = index_koincidencie(sifra)
```

Tu `sifra` nie je ďalší údaj, ktorý máš zadať do terminálu. Je to premenná, ktorú program už vytvoril z načítaného súboru. Pri volaní dostane funkcia jej hodnotu do svojho parametra `text`:

```python
def index_koincidencie(text: str) -> float:
    ...
```

`return` potom vráti vypočítané číslo späť do `main()` a uloží sa do premennej `ik`. Takto fungujú aj ostatné funkcie: jedna vráti výsledok, ďalšia ho dostane ako vstup.

## 1. Čo riešime

Máme štyri zašifrované súbory. Potrebujeme určiť heslo každého z nich a získať pôvodný text. Zadanie hovorí, že:

- šifrujú sa iba veľké písmená `A` až `Z`;
- heslo má 15 až 25 písmen;
- pôvodný text môže byť slovenský alebo anglický;
- medzery a ďalšie formátovacie znaky sa pri šifrovaní ignorujú.

V abecede používame čísla `A = 0`, `B = 1`, …, `Z = 25`. Pri šifrovaní sa číslo písmena textu a písmena hesla sčíta. Pri dešifrovaní sa číslo hesla odčíta:

```text
šifrovanie:    C = (P + K) mod 26
dešifrovanie:  P = (C - K) mod 26
```

`P` je písmeno pôvodného textu, `C` písmeno šifry a `K` písmeno hesla. `mod 26` znamená, že výsledok zostane medzi 0 a 25. Napríklad `A - B` je `0 - 1 = -1`, ale `-1 mod 26 = 25`, teda `Z`.

Heslo sa opakuje. Pri hesle `ABC` šifruje prvé písmeno textu `A`, druhé `B`, tretie `C`, štvrté opäť `A` atď. Preto musíme najskôr zistiť **dĺžku hesla**, potom **jednotlivé písmená hesla**.

## 2. Celý postup v skratke

```text
načítanie súboru
    ↓
výber písmen A–Z
    ↓
IK celého textu a Kasiskiho opakované trojice
    ↓
skúšanie dĺžok hesla 15–25 pomocou IK skupín
    ↓
výber najpravdepodobnejšej dĺžky
    ↓
skúšanie 26 posunov pre každé písmeno hesla
    ↓
porovnanie slovenčiny a angličtiny
    ↓
dešifrovanie modulo 26
    ↓
vrátenie pôvodných medzier a výpis výsledku
```

Kasiskiho metóda a index koincidencie dávajú **štatistické odhady**. Nie sú dôkazom, že každé písmeno hesla musí byť správne. Výsledný text preto kontrolujeme aj podľa toho, či dáva zmysel.

### Jedno konkrétne spustenie: `text1_enc.txt`

Táto tabuľka ukazuje, odkiaľ sa berie každý vstup funkcie. Hodnoty sú skrátené, aby sa dali prečítať.

| Poradie | Čo sa vykoná | Čo dostane | Čo vznikne |
| ---: | --- | --- | --- |
| 1 | `read_text()` | cesta `text1_enc.txt` z terminálu | `povodny_text`, začína `ENEEZC TIQPL...` |
| 2 | `priprav_sifru(povodny_text)` | celý obsah súboru s medzerami | `sifra`, začína `ENEEZCTIQPL...` a má 637 písmen |
| 3 | `index_koincidencie(sifra)` | súvislá šifra | `ik = 0,0402` |
| 4 | `kasiski_zhody(sifra)` | súvislá šifra | `zhody`, napríklad trojica `CIW` na pozíciách 84 a 126, vzdialenosť 42 |
| 5 | `kandidati_dlzky(sifra, zhody)` | šifra a zoznam vzdialeností | pre dĺžku 15 vyjde 6 deliteľných vzdialeností a priemerný IK skupín `0,0613` |
| 6 | `odhadni_dlzku(kandidati)` | výsledky pre dĺžky 15–25 | `odhad_dlzky = 15` |
| 7 | `porovnaj_jazyky(sifra, dlzka)` | šifra a zvolená dĺžka 15 | slovenský a anglický návrh hesla so skóre |
| 8 | výber lepšieho návrhu v `main()` | oba návrhy | `jazyk = SK`, `heslo = QWERTYUIOPASDFG` |
| 9 | `desifruj(sifra, heslo)` | šifra a vybrané heslo | `otvoreny_text`, začína `ORANGEZACAL...` |
| 10 | `vrat_formatovanie(povodny_text, otvoreny_text)` | pôvodný súbor a súvislý dešifrovaný text | `zobrazeny_text`, začína `ORANGE ZACAL...` |

Niektoré riadky majú vnútri ďalšie volania. `kandidati_dlzky()` volá `priemerny_ik_skupin()`, tá volá `rozdel_na_skupiny()` a `index_koincidencie()`. Neskôr `porovnaj_jazyky()` volá `odhadni_heslo()` pre oba jazyky; táto funkcia rozdelí šifru na skupiny a pre každú skúsi 26 posunov cez `ohodnot_posuny()` a `frekvencie()`. Pre prvý text vyjde priemerné slovenské skóre `-2,9630` a anglické `-3,0786`. Vyššie je `-2,9630`, preto `main()` zvolí slovenčinu. Pri čítaní kódu môžeš začať v `main()` a pri každom volaní sa pozrieť na príslušnú funkciu.

## 3. Načítanie a príprava textu

### `je_sifrovane_pismeno(znak)`

**Vstup:** jeden znak. **Výstup:** `True` alebo `False`.

Funkcia kontroluje, či je znak medzi veľkými písmenami `A` a `Z`. Napríklad pre `"M"` vráti `True`, pre medzeru `False`. V aktuálnom kóde malé písmená neprepúšťa, čo zodpovedá súborom v tomto zadaní.

```python
return "A" <= znak and znak <= "Z"
```

Python porovnáva znaky podľa ich číselných kódov. Tento riadok ešte nepriraďuje písmenu číslo 0 až 25; iba testuje rozsah. Funkciu volá `priprav_sifru()` pri výbere písmen a `vrat_formatovanie()` pri vkladaní medzier späť. Samostatná funkcia nám zaručuje rovnaké pravidlo na oboch miestach.

### `priprav_sifru(povodny_text)`

**Vstup:** celý obsah súboru vrátane medzier. **Výstup:** súvislý reťazec veľkých písmen A–Z.

Najprv `replace(" ", "")` odstráni medzery. Potom `for` prejde text znak po znaku. Ak `je_sifrovane_pismeno(znak)` vráti `True`, pripojí znak do premennej `sifra`. Ostatné znaky preskočí.

```python
sifra = ""
for znak in text_bez_medzier:
    if je_sifrovane_pismeno(znak):
        sifra += znak
```

Napríklad z `"ABC DE!F"` vznikne `"ABCDEF"`. Pôvodný text si nechávame osobitne, aby sme na konci mohli vrátiť jeho medzery. Heslo sa posúva iba pri šifrovaných písmenách, nie pri medzerách.

## 4. Index koincidencie celého textu

### `index_koincidencie(text)`

**Vstup:** text z písmen A–Z. **Výstup:** desatinné číslo od 0 do 1.

Index koincidencie (IK) je pravdepodobnosť, že dve písmená vybrané z **rôznych pozícií** budú rovnaké. Pri `ABCD` je IK 0, lebo každé písmeno je iné. Pri `AAAA` je IK 1, lebo každá dvojica sa zhoduje.

Funkcia pripraví pole `pocet` s 26 nulami. Položka `pocet[0]` patrí písmenu `A`, položka `pocet[1]` písmenu `B` atď. Výraz `ord(znak) - ord("A")` prevedie písmeno na index 0 až 25. `ord()` vracia číselný kód znaku; odpočítaním kódu `A` dostaneme `A = 0`.

```python
pocet[ord(znak) - ord("A")] += 1
spolu += 1
```

`spolu` je celkový počet písmen. Potom sa použije vzorec:

```text
IK = [súčet nᵢ × (nᵢ − 1) pre všetkých 26 písmen] / [N × (N − 1)]
```

`nᵢ` je počet výskytov jedného písmena, `N` je počet všetkých písmen. Prvé písmeno dvojice možno vybrať z `N` pozícií a druhé z `N - 1`, pretože nesmieme vybrať tú istú pozíciu znova. Rovnaká logika platí pre `nᵢ × (nᵢ - 1)` pri jednom konkrétnom písmene.

Príklad `AAB`: `A` má počet 2, `B` počet 1. Čitateľ je `2 × 1 + 1 × 0 = 2`, menovateľ `3 × 2 = 6`, takže IK je `2/6 = 0,3333`.

V Pythone čitateľ vytvára `sum(n * (n - 1) for n in pocet)`: `for` prejde počty všetkých písmen a `sum()` výsledky sčíta. Ak má text menej než dve písmená, funkcia vyhodí `ValueError`, lebo by sa delilo nulou.

IK celých našich šifier je približne `0,04`. Pri približne rovnomerných písmenách A–Z je očakávaná hodnota `1/26 ≈ 0,0385`. Celá Vigenèrova šifra mieša viac posunov, a preto samotný IK ešte heslo neurčí. Najviac nám pomôže až pri **skupinách**.

## 5. Kasiskiho metóda

### `kasiski_zhody(text)`

**Vstup:** očistená šifra. **Výstup:** zoznam opakovaných trojíc a vzdialeností medzi nimi.

Funkcia prejde každú pozíciu, na ktorej sa začína trojica. `text[pozicia : pozicia + 3]` vyberie tri po sebe idúce písmená. `range(len(text) - 2)` skončí tak, aby trojica nepresiahla koniec textu.

Slovník `pozicie` si pamätá, kde sa každá trojica už objavila. Napríklad pri texte `ABCXYZABC` uvidíme `ABC` na pozíciách 0 a 6. Funkcia uloží vzdialenosť `6 - 0 = 6`.

```python
pozicie: dict[str, list[int]] = {}
```

Kľúč slovníka je trojica, napríklad `"ABC"`; hodnotou je zoznam pozícií, napríklad `[0, 6]`. `pozicie.get(trojica, [])` vráti staršie pozície alebo prázdny zoznam. `setdefault(trojica, []).append(pozicia)` založí zoznam pri prvom výskyte a pridá aktuálnu pozíciu.

Každú zhodu funkcia vráti ako štvoricu `(trojica, prvá_pozícia, druhá_pozícia, vzdialenosť)`. `append()` pridáva tieto štvorice do zoznamu `zhody`.

Ak sa rovnaký kúsok pôvodného textu zašifruje v rovnakej fáze hesla, jeho výskyty v šifre môžu byť rovnaké a ich vzdialenosť býva násobkom dĺžky hesla. Nie každá opakovaná trojica má túto príčinu; niektoré vzniknú náhodou. Viac susedných trojíc z jedného opakovaného úseku tiež nie je viac nezávislých dôkazov.

## 6. Skúšanie dĺžky hesla

### `rozdel_na_skupiny(text, dlzka_hesla)`

**Vstup:** očistená šifra a skúšaná dĺžka hesla. **Výstup:** zoznam skupín písmen.

Pri hesle dĺžky 3 patria do jednej skupiny pozície 0, 3, 6…, do ďalšej 1, 4, 7… a do tretej 2, 5, 8…. Všetky písmená jednej skupiny by boli šifrované tým istým písmenom hesla.

```python
text[i::dlzka_hesla]
```

Rez reťazca má tvar `[začiatok:koniec:krok]`. Tu sa začína na `i`, koniec je vynechaný (ide sa až po koniec textu) a krok je `dlzka_hesla`. `range(dlzka_hesla)` dá všetky začiatky od 0 po `dlzka_hesla - 1`. Napríklad `ABCDEFGHIJKL` pri dĺžke 3 dá skupiny `ADGJ`, `BEHK`, `CFIL`.

### `priemerny_ik_skupin(text, dlzka_hesla)`

**Vstup:** šifra a skúšaná dĺžka. **Výstup:** priemer IK všetkých skupín.

Funkcia zavolá `rozdel_na_skupiny()`, vypočíta `index_koincidencie()` každej skupiny, hodnoty sčíta a vydelí počtom skupín. Pri správnej dĺžke hesla je každá skupina šifrovaná jedným Caesarovým posunom. Tento posun síce premenuje písmená, ale **nemení počet zhôd**. IK skupín preto zvyčajne narastie oproti IK celej šifry.

### `kandidati_dlzky(text, zhody)`

**Vstup:** šifra a Kasiskiho zhody. **Výstup:** zoznam trojíc `(dĺžka, počet deliteľných vzdialeností, priemerný IK)`.

Funkcia skúša dĺžky od 15 do 25, lebo to určuje zadanie. `range(15, 26)` zahŕňa 15 až 25; horná hranica 26 sa už nevykoná. Pri každej dĺžke:

1. Spočíta, koľko Kasiskiho vzdialeností je deliteľných dĺžkou. Výraz `vzdialenost % dlzka == 0` znamená, že po delení nezostane zvyšok.
2. Vypočíta priemerný IK skupín pre túto dĺžku.

Ak je text pre niektorú dĺžku príliš krátky, funkcia ju preskočí; v každej skupine potrebujeme aspoň dve písmená na výpočet IK.

### `odhadni_dlzku(kandidati)`

**Vstup:** kandidáti z predchádzajúcej funkcie. **Výstup:** jedna vybraná dĺžka hesla.

`max(..., key=...)` vyberie kandidáta s najvyšším priemerným IK. Ak sa IK dvoch kandidátov presne zhoduje, rozhodne vyšší počet Kasiskiho vzdialeností. V našich štyroch súboroch vychádzajú dĺžky 15, 25, 19 a 17. Kasiskiho počty skript vypisuje, ale pri bežnom výbere má prednosť IK skupín.

## 7. Určenie písmen hesla

### `frekvencie(text)`

**Vstup:** jedna skupina písmen. **Výstup:** pole 26 počtov pre `A` až `Z`.

Používa rovnaké indexovanie cez `ord(znak) - ord("A")` ako IK. Toto pole však potrebujeme na iný účel: porovnávame **celé rozloženie písmen**, nielen počet zhôd. Napríklad z `AABC` vznikne počet `A:2`, `B:1`, `C:1` a ostatné počty sú nula.

### `ohodnot_posuny(skupina, jazykove_pocty)`

**Vstup:** jedna skupina šifry a frekvenčný profil jazyka. **Výstup:** všetkých 26 možných písmen hesla zoradených podľa skóre.

Každú skupinu šifrovalo jedno písmeno hesla, teda jeden Caesarov posun. Funkcia skúsi posuny `A = 0` až `Z = 25`. Pre každý posun zistí, ako by po dešifrovaní vyzerali počty písmen, a porovná ich s frekvenciami bežného jazyka.

`SLOVENSKE_POCTY` sú počty z dodanej tabuľky s 1997 písmenami. `ANGLICKE_POCTY` pochádzajú zo [súboru anglických monogramov](https://people.math.sc.edu/Burkardt/datasets/ngrams/english_monograms.txt). Sú to vzorky jazyka, nie pevné pravidlá pre každý text.

Z počtu výskytov sa vytvorí pravdepodobnosť písmena:

```text
písmeno má pravdepodobnosť (jeho počet + 1) / (súčet všetkých počtov + 26)
```

Pridanie jednotky zabraňuje nulovej pravdepodobnosti pri písmene, ktoré sa vo vzorke nevyskytlo. Bez toho by `math.log(0)` nebolo možné vypočítať.

Skóre posunu je súčet `počet_výskytov × log(pravdepodobnosť)` cez 26 písmen. `math.log()` je prirodzený logaritmus. Väčšina skóre je záporná; **vyššie skóre (bližšie k nule) je lepšie**. Funkcia preto použije `sorted(..., reverse=True)`. Toto skóre nehovorí, že posun je určite správny; iba porovnáva, ako dobre sedí na jazykový profil.

### `odhadni_heslo(text, dlzka_hesla, jazykove_pocty)`

**Vstup:** šifra, vybraná dĺžka a jeden jazykový profil. **Výstup:** návrh hesla a jeho celkové skóre.

Funkcia rozdelí text na skupiny, pre každú zavolá `ohodnot_posuny()` a vezme prvý, najlepšie hodnotený posun. Tieto písmená spojí do hesla. Keď má heslo dĺžku 15, získa 15 skupín a z nich 15 písmen hesla. Skóre najlepších posunov sčíta, aby sa dali porovnať jazykové profily.

### `porovnaj_jazyky(text, dlzka)`

**Vstup:** šifra a vybraná dĺžka. **Výstup:** slovenský a anglický návrh hesla so skóre.

Zavolá `odhadni_heslo()` dvakrát: raz so slovenskými počtami a raz s anglickými. V `main()` sa vyberie profil s vyšším celkovým skóre. Skóre sa pri výpise delí dĺžkou textu, aby sa čítalo ako priemerné skóre na jedno písmeno. Tým, že sa porovnávajú oba jazyky, skript nemusí mať jazyk zadaný vopred.

## 8. Dešifrovanie a formátovanie

### `desifruj(sifra, heslo)`

**Vstup:** súvislá šifra A–Z a heslo A–Z. **Výstup:** súvislý dešifrovaný text bez medzier.

Funkcia najprv overí, že heslo obsahuje len platné písmená. Potom pri každom písmene šifry vezme zodpovedajúce písmeno hesla. Výraz `i % len(heslo)` vracia pozíciu v hesle a po poslednom písmene sa vráti na začiatok.

```python
heslo[i % len(heslo)]
```

Čísla písmen sa odčítajú modulo 26. V kóde je použitý `ord()` na získanie číselných kódov a `chr()` na zmenu výsledného čísla späť na znak. Rozdiel `ord(pismeno) - ord(pismeno_hesla)` je rovnaký ako rozdiel ich pozícií v abecede, lebo spoločný základ `ord("A")` sa pri odčítaní vyruší.

### `vrat_formatovanie(povodny_text, otvoreny_text)`

**Vstup:** pôvodný obsah šifrovaného súboru a súvislý dešifrovaný text. **Výstup:** dešifrovaný text s pôvodnými medzerami a ďalšími nešifrovanými znakmi.

Funkcia prechádza pôvodný text. Premenná `pozicia` ukazuje na ďalšie dešifrované písmeno. Ak nájde v pôvodnom texte písmeno A–Z, vloží namiesto neho `otvoreny_text[pozicia]` a zvýši `pozicia`. Ak nájde medzeru alebo iný znak, ponechá ho. Znaky sa ukladajú do zoznamu cez `append()` a na konci sa spoja pomocou `"".join(vysledok)`.

Príklad: pôvodná šifra `ABC DEF`, súvislý dešifrovaný text `XYZUVW`, výsledok `XYZ UVW`. Kontroly s `ValueError` zisťujú, či počet dešifrovaných písmen sedí s počtom písmen v pôvodnom texte. Funkcia sama heslo neurčuje ani nič nedešifruje.

## 9. `main()` spája kroky

`main()` je funkcia, ktorá volá ostatné funkcie v správnom poradí. Začína spracovaním argumentov príkazového riadku cez `argparse`. `Path` reprezentuje cestu k súboru a `read_text(encoding="utf-8")` prečíta jeho obsah. `try`/`except` zachytí chyby, napríklad neexistujúci súbor alebo neplatné heslo, a `parser.error()` vypíše zrozumiteľnú hlášku.

V `main()` sa potom vykoná tento sled:

1. Načíta sa pôvodný súbor a zavolá `priprav_sifru()`.
2. Vypočíta sa IK celého textu.
3. Nájdu sa Kasiskiho opakované trojice.
4. Skúsia sa dĺžky 15 až 25 a zvolí sa odhad dĺžky.
5. Vytvorí sa návrh hesla pre slovenčinu aj angličtinu a vyberie sa lepšie skóre.
6. Vypíšu sa skupiny, ich frekvencie a najlepšie posuny.
7. Zavolá sa `desifruj()` a potom `vrat_formatovanie()`.
8. Vypíše sa heslo a dešifrovaný text; pri `--vystup` sa text aj uloží.

Zápis na konci súboru `if __name__ == "__main__": main()` zabezpečí, že sa `main()` spustí, keď skript spustíme priamo. Ak by sme súbor načítali ako modul z iného programu, funkcie budú dostupné, ale `main()` sa nespustí automaticky.

## 10. Voliteľné argumenty príkazu

Základný príkaz je na začiatku návodu. Bez ďalších argumentov skript vypíše analýzu, odhadnuté heslo aj dešifrovaný text. Ak chceš ručne vyskúšať inú možnosť alebo uložiť výsledok, použi jeden z týchto argumentov:

```bash
# Vyskúšaj inú dĺžku hesla:
python3 "T1 - Viegenerovská šifra/riesenie.py" "T1 - Viegenerovská šifra/text1_enc.txt" --dlzka 15

# Použi vlastné heslo:
python3 "T1 - Viegenerovská šifra/riesenie.py" "T1 - Viegenerovská šifra/text1_enc.txt" --heslo QWERTYUIOPASDFG

# Ulož dešifrovaný text do súboru:
python3 "T1 - Viegenerovská šifra/riesenie.py" "T1 - Viegenerovská šifra/text1_enc.txt" --vystup "T1 - Viegenerovská šifra/text1_dec.txt"
```

`--dlzka` a `--heslo` umožňujú ručne overiť iný odhad. `--vystup` zapíše dešifrovaný text do zvolenej cesty. Bez `--vystup` sa nič nezapisuje, výsledok sa iba vypíše v termináli.

## 11. Výsledok pre dodané súbory

| Súbor | Zvolený profil | Dĺžka hesla | Heslo |
| --- | --- | ---: | --- |
| `text1_enc.txt` | SK | 15 | `QWERTYUIOPASDFG` |
| `text2_enc.txt` | SK | 25 | `AUZDMZRNFUXQSXHORWQLCLZLS` |
| `text3_enc.txt` | SK | 19 | `LIYZKFOREGYSDTRQNTK` |
| `text4_enc.txt` | EN | 17 | `IDGKZQNOMYNTJOUIB` |

Dešifrované texty sú v súboroch `text1_dec.txt` až `text4_dec.txt`. Prvé tri sú po slovensky bez diakritiky, štvrtý je po anglicky. Pri inej šifre môže byť štatistický odhad nepresný, zvlášť ak je text krátky alebo má nezvyčajné rozloženie písmen. Vtedy treba skontrolovať aj čitateľnosť výsledku a prípadne vyskúšať ďalší kandidátsky posun alebo dĺžku.

## 12. Prvky Pythonu, ktoré sa tu oplatí zapamätať

| Zápis | Čo robí | Kde ho vieš použiť znova |
| --- | --- | --- |
| `def nazov(vstup):` | Definuje funkciu s vlastným vstupom. | Rozdelenie väčšieho problému na malé kroky. |
| `: str`, `-> bool` | Typové anotácie pre čitateľa a nástroje; Python ich sám nevynucuje. | Keď chceš jasne ukázať, čo funkcia prijíma a vracia. |
| `return` | Vráti hodnotu z funkcie. | Pri výpočte hodnoty, ktorú použije ďalší krok. |
| `for znak in text` | Postupne spracuje znaky textu. | Pri filtrovaní a počítaní znakov. |
| `range(15, 26)` | Vytvorí čísla 15 až 25. | Pri skúšaní konečného rozsahu možností. |
| `text[i::k]` | Vezme každý `k`-ty znak od pozície `i`. | Pri rozdeľovaní dát do pravidelných skupín. |
| `ord()` / `chr()` | Prevedie znak na číselný kód / číslo na znak. | Pri práci s abecedou, znakmi a kódovaním. |
| `%` | Vráti zvyšok po delení. | Pri cyklickom opakovaní hesla a pri modulo 26. |
| `dict`, `.get()`, `.setdefault()` | Ukladá a vyhľadáva hodnoty podľa kľúča. | Keď si treba pamätať, kde sa určitý jav už vyskytol. |
| `list`, `.append()`, `"".join()` | Zbiera časti a potom ich spojí do textu. | Pri skladaní výsledku z mnohých znakov. |
| `sum()`, `max()`, `sorted()` | Sčíta, vyberie najväčšiu hodnotu, zoradí. | Pri vyhodnocovaní viacerých kandidátov. |
| `try` / `except` | Zachytí očakávanú chybu. | Pri čítaní súborov a kontrole vstupov. |
| `f"...{hodnota}..."` | Vloží hodnotu premennej do textu. | Pri výpise výsledkov a chybových hlášok. |

Pri štúdiu je užitočné sledovať jednu hodnotu — napríklad `sifra` — od načítania cez jednotlivé funkcie až po dešifrovaný text. Tak vidíš, čo každý krok dostane a čo odovzdá ďalšiemu.
