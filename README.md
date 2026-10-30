# Projekt 1 – Uczenie Maszynowe (Etap 1: Analiza danych)

Analiza eksploracyjna dwóch zbiorów danych o rynku mieszkań w Polsce: danych liczbowych (Kaggle) i danych w języku naturalnym (Hugging Face / Otodom). Oba zbiory zawierają dane rzeczywiste (ogłoszenia opublikowane w serwisach nieruchomości), a nie dane symulowane.

## Dane

| | Zbiór 1 (dane liczbowe) | Zbiór 2 (dane tekstowe) |
|---|---|---|
| Plik w repozytorium | `data/apartments_pl_2023_08.csv` | `data/sample.parquet` |
| Rozmiar | 18 905 wierszy × 28 kolumn | 100 wierszy × 51 kolumn |
| Zawartość | oferty sprzedaży mieszkań z 15 największych miast, sierpień 2023 | ogłoszenia z Otodom.pl, wyłącznie Warszawa, zebrane 15.05.2026 |
| Źródło | [Kaggle: Apartment Prices in Poland](https://www.kaggle.com/datasets/krzysztofjamroz/apartment-prices-in-poland) (autor: Krzysztof Jamroz) | [Hugging Face: logiover/otodom-pl-scraper-polish-real-estate-data-sample-data](https://huggingface.co/datasets/logiover/otodom-pl-scraper-polish-real-estate-data-sample-data) |

Schemat kolumn zbioru 2 odpowiada danym zwracanym przez narzędzie [Otodom.pl Scraper](https://apify.com/logiover/otodom-pl-scraper-polish-real-estate-data) (Apify).

**Podzbiory i sposób ich uzyskania**

- Zbiór 1: jeden z 11 plików miesięcznych (`apartments_pl_2023_08.csv`, oferty sprzedaży), użyty w całości, bez losowania i filtrowania wierszy. Pobranie: strona Kaggle, przycisk *Download*, rozpakowanie archiwum i skopiowanie pliku do `data/`.
- Zbiór 2: cały dostępny plik `sample.parquet` (100 ogłoszeń). Pobranie: strona zbioru na Hugging Face, zakładka *Files and versions*, plik do `data/`.

## Struktura repozytorium

```
├── README.md
├── requirements.txt
├── generate_figures.py     # wykresy 1–4 (zbiór 1)
├── analiza_tekstu.py       # analiza tekstu i wykresy 5–6 (zbiór 2)
├── data/
│   ├── apartments_pl_2023_08.csv
│   └── sample.parquet
└── figures/
    ├── wykres1_rozklad_cen.png
    ├── wykres2_cena_vs_powierzchnia.png
    ├── wykres3_top5_miast.png
    ├── wykres4_mediana_cena_za_m2_miasta.png
    ├── wykres5_dlugosc_tekstow.png
    └── wykres6_najczestsze_slowa.png
```

## Uruchomienie

```bash
pip install -r requirements.txt
python generate_figures.py   # statystyki i wykresy dla zbioru 1
python analiza_tekstu.py     # długość tekstów, najczęstsze słowa, duplikaty, wykresy dla zbioru 2
```

Skrypty należy uruchamiać z katalogu głównego repozytorium. Wykresy zapisywane są w folderze `figures/`, a statystyki wypisywane w konsoli.

## Wykresy

1. `wykres1_rozklad_cen.png`: rozkład cen ofertowych (zbiór 1)
2. `wykres2_cena_vs_powierzchnia.png`: cena a powierzchnia, korelacje Pearsona i Spearmana (zbiór 1)
3. `wykres3_top5_miast.png`: pięć miast z największą liczbą ofert (zbiór 1)
4. `wykres4_mediana_cena_za_m2_miasta.png`: mediana ceny za m² w 15 miastach, test Kruskala–Wallisa (zbiór 1)
5. `wykres5_dlugosc_tekstow.png`: długość `title` i `shortDescription` (zbiór 2)
6. `wykres6_najczestsze_slowa.png`: 15 najczęstszych słów bez stopwords (zbiór 2)

## Licencje danych

(Zbiór1)Licencja: Apache License 2.0 (https://www.apache.org/licenses/LICENSE-2.0), zgodnie z informacją na stronie zbioru.
(Zbiór2)Licencja: CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), zgodnie z metadanymi zbioru na Hugging Face. Autor: Logiover.