#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

/* 2. načítanie zašifrovaného súboru */
static uint8_t *nacitaj_subor(const char *cesta, size_t *dlzka)
{
    FILE *f = fopen(cesta, "rb");
    if (!f) {
        perror(cesta);
        return NULL;
    }
    if (fseek(f, 0, SEEK_END) != 0) {
        perror(cesta);
        fclose(f);
        return NULL;
    }
    long velkost = ftell(f);
    if (velkost <= 0 || (uintmax_t)velkost > SIZE_MAX || fseek(f, 0, SEEK_SET) != 0) {
        fprintf(stderr, "Chyba: Subor je prazdny alebo sa neda zistit jeho velkost.\n");
        fclose(f);
        return NULL;
    }
    *dlzka = (size_t)velkost;
    uint8_t *data = malloc(*dlzka);
    if (!data) {
        fprintf(stderr, "Chyba: Nedostatok pamate.\n");
        fclose(f);
        return NULL;
    }
    size_t precitane = fread(data, 1, *dlzka, f);
    int chyba = ferror(f);
    fclose(f);
    if (chyba || precitane != *dlzka) {
        fprintf(stderr, "Chyba pri citani '%s'.\n", cesta);
        free(data);
        return NULL;
    }
    return data;
}

/* 4. vytvorenie 256-bajtového kľúča z hesla a inicializácia stavu RC4 */
static void get_key(const char *heslo, uint8_t kluc[256])
{
    size_t dlzka = strlen(heslo);
    for (size_t i = 0; i < 256; ++i)
        kluc[i] = (uint8_t)heslo[i % dlzka];
}

static void rc4_init(const uint8_t kluc[256], uint8_t stav[256])
{
    unsigned j = 0;
    for (unsigned i = 0; i < 256; ++i)
        stav[i] = (uint8_t)i;
    for (unsigned i = 0; i < 256; ++i) {
        j = (j + stav[i] + kluc[i]) % 256;
        uint8_t tmp = stav[i];
        stav[i] = stav[j];
        stav[j] = tmp;
    }
}

/* 5. vyhenerovanie pseudonáhodného prúdu a desifrovanie pomocou XOR */
static void generuj_prud(uint8_t stav[256], size_t dlzka,
                         uint8_t *prud)
{
    unsigned i = 0, j = 0;
    for (size_t n = 0; n < dlzka; ++n) {
        i = (i + 1) % 256;
        j = (j + stav[i]) % 256;
        uint8_t tmp = stav[i];
        stav[i] = stav[j];
        stav[j] = tmp;
        prud[n] = stav[(stav[i] + stav[j]) % 256];
    }
}

static void desifruj(const uint8_t *sifra, const uint8_t *prud,
                    size_t dlzka, uint8_t *text)
{
    for (size_t i = 0; i < dlzka; ++i)
        text[i] = sifra[i] ^ prud[i];
}

/* 6. odhadnutie desifrovaneho textu */
static int vyzera_ako_text(const uint8_t *data, size_t dlzka)
{
    size_t i = 0;
    while (i < dlzka) {
        uint32_t znak = data[i++], minimum = 0;
        unsigned dalsie = 0;
        if (znak >= 0xc2 && znak <= 0xdf) {
            znak &= 0x1f; dalsie = 1; minimum = 0x80;
        } else if (znak >= 0xe0 && znak <= 0xef) {
            znak &= 0x0f; dalsie = 2; minimum = 0x800;
        } else if (znak >= 0xf0 && znak <= 0xf4) {
            znak &= 7; dalsie = 3; minimum = 0x10000;
        } else if (znak >= 0x80) {
            return 0;
        }
        if (dalsie > dlzka - i)
            return 0;
        for (unsigned n = 0; n < dalsie; ++n) {
            uint8_t b = data[i++];
            if ((b & 0xc0) != 0x80)
                return 0;
            znak = (znak << 6) | (b & 0x3f);
        }
        if (znak < minimum || znak > 0x10ffff || (znak >= 0xd800 && znak <= 0xdfff))
            return 0;
    }
    return dlzka != 0;
}

/* 7. ulozenie kandidatov do suboru */
static int uloz_subor(const char *cesta, const uint8_t *data, size_t dlzka,
                     const char *heslo, double cas)
{
    FILE *f = fopen(cesta, "wb");
    if (!f)
        return 0;
    int ok = fprintf(f, "Heslo: %s\nCas prelamovania: %.0f s\n\n", heslo, cas) >= 0;
    if (ok)
        ok = fwrite(data, 1, dlzka, f) == dlzka;
    int chyba = errno;
    if (fclose(f) != 0)
        return 0;
    if (!ok)
        errno = chyba;
    return ok;
}

/* 3. hladanie hesla */
static int najdi_hesla(const uint8_t *sifra, size_t dlzka, const char *cesta)
{
    char vystup[4096];
    uint8_t *text = malloc(dlzka);
    if (!text) {
        fprintf(stderr, "Chyba: Nedostatok pamate.\n");
        return 0;
    }
    unsigned pocet = 0;
    time_t zaciatok = time(NULL);
    for (unsigned cislo = 10000000; cislo < 100000000; ++cislo) {
        char heslo[9];
        uint8_t kluc[256], stav[256];
        snprintf(heslo, sizeof heslo, "%08u", cislo);
        get_key(heslo, kluc);
        rc4_init(kluc, stav);
        generuj_prud(stav, dlzka, text);
        desifruj(sifra, text, dlzka, text);
        if (vyzera_ako_text(text, dlzka)) {
            double cas = difftime(time(NULL), zaciatok);
            snprintf(vystup, sizeof vystup, "%s_heslo_%s_dec.txt", cesta, heslo);
            if (!uloz_subor(vystup, text, dlzka, heslo, cas)) {
                fprintf(stderr, "Chyba pri zapise '%s': %s\n", vystup, strerror(errno));
                free(text);
                return 0;
            }
            ++pocet;
            printf("Heslo: %s\nCas do najdenia: %.0f s\nVysledok ulozeny do: %s\n",
                   heslo, cas, vystup);
        }
        if (cislo % 10000 == 0)
            printf("Skusam heslo: %s\n", heslo);
    }
    printf("\nHotovo. Pocet kandidatov: %u\n", pocet);
    printf("Celkovy cas prelamovania: %.0f s\n", difftime(time(NULL), zaciatok));
    free(text);
    return 1;
}

/* 1. main */
int main(int argc, char **argv)
{
    if (argc != 2) {
        fprintf(stderr, "Pouzitie: %s subor\n", argv[0]);
        return EXIT_FAILURE;
    }
    size_t dlzka;
    uint8_t *sifra = nacitaj_subor(argv[1], &dlzka);
    if (!sifra)
        return EXIT_FAILURE;
    int uspech = najdi_hesla(sifra, dlzka, argv[1]);
    /* 8. návrat do main */
    free(sifra);
    return uspech ? EXIT_SUCCESS : EXIT_FAILURE;
}
