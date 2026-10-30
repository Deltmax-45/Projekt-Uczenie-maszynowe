"""
Projekt 1 - Uczenie Maszynowe (Etap 1: Analiza danych)
Generowanie wykresów EDA dla zbioru 1 (Apartment Prices in Poland, sierpień 2023).

Uruchomienie (z katalogu głównego repozytorium):
    python generate_figures.py
Wymaga pliku data/apartments_pl_2023_08.csv. Wykresy trafiają do folderu figures/.
"""

import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.ticker import FuncFormatter
from scipy import stats

DATA_PATH = "data/apartments_pl_2023_08.csv"
FIG_DIR = "figures"
os.makedirs(FIG_DIR, exist_ok=True)

sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["axes.labelsize"] = 12
COLOR = "#2f6db5"
COLOR_ACCENT = "#d1495b"

CITY_NAMES = {
    "warszawa": "Warszawa", "krakow": "Kraków", "gdansk": "Gdańsk",
    "wroclaw": "Wrocław", "gdynia": "Gdynia", "poznan": "Poznań",
    "rzeszow": "Rzeszów", "lublin": "Lublin", "bialystok": "Białystok",
    "szczecin": "Szczecin", "lodz": "Łódź", "katowice": "Katowice",
    "bydgoszcz": "Bydgoszcz", "radom": "Radom", "czestochowa": "Częstochowa",
}


def comma(value, digits=2):
    """Liczba z przecinkiem dziesiętnym (polski zapis), np. 0,64."""
    return f"{value:.{digits}f}".replace(".", ",")


def spaced(x, _pos=None):
    """Liczba z odstępem tysięcznym (polski zapis), np. 1 000."""
    return f"{x:,.0f}".replace(",", " ")


df = pd.read_csv(DATA_PATH)
print(f"Liczba wierszy w zbiorze 1: {df.shape[0]}")
print(f"Liczba kolumn w zbiorze 1: {df.shape[1]}")
df["city_pl"] = df["city"].map(CITY_NAMES)
df["price_per_sqm"] = df["price"] / df["squareMeters"]


# --- Wykres 1: rozkład cen ---
price_k = df["price"] / 1000
mean_k, median_k = price_k.mean(), price_k.median()

fig, ax = plt.subplots()
sns.histplot(price_k, bins=50, kde=True, color=COLOR, ax=ax)
ax.axvline(mean_k, color=COLOR_ACCENT, linestyle="--", linewidth=2,
           label=f"Średnia: {spaced(mean_k)} tys. zł")
ax.axvline(median_k, color="black", linestyle=":", linewidth=2,
           label=f"Mediana: {spaced(median_k)} tys. zł")
ax.set_title("Rozkład cen ofertowych mieszkań (sierpień 2023)")
ax.set_xlabel("Cena [tys. zł]")
ax.set_ylabel("Liczba ofert")
ax.xaxis.set_major_formatter(FuncFormatter(spaced))
ax.yaxis.set_major_formatter(FuncFormatter(spaced))
ax.legend()
fig.tight_layout()
fig.savefig(f"{FIG_DIR}/wykres1_rozklad_cen.png", dpi=200)
plt.close(fig)
print(f"Skośność ceny: {df['price'].skew():.2f}")
print(f"Średnia cena [zł]: {df['price'].mean():.0f}")
print(f"Mediana ceny [zł]: {df['price'].median():.0f}")


# --- Wykres 2: cena a powierzchnia ---
r, p = stats.pearsonr(df["squareMeters"], df["price"])
rho, _ = stats.spearmanr(df["squareMeters"], df["price"])

fig, ax = plt.subplots()
sns.scatterplot(data=df, x="squareMeters", y=price_k, alpha=0.25, s=12,
                color=COLOR, edgecolor=None, ax=ax)
sns.regplot(data=df, x="squareMeters", y=price_k, scatter=False,
            line_kws={"color": COLOR_ACCENT, "linewidth": 2.5}, ax=ax)
ax.set_title("Cena a powierzchnia mieszkania")
ax.set_xlabel("Powierzchnia [m²]")
ax.set_ylabel("Cena [tys. zł]")
ax.yaxis.set_major_formatter(FuncFormatter(spaced))
ax.text(0.03, 0.95, f"Pearson r = {comma(r)} (R² = {comma(r**2)})\nSpearman ρ = {comma(rho)}",
        transform=ax.transAxes, va="top", fontsize=12,
        bbox={"boxstyle": "round", "facecolor": "white", "edgecolor": "gray"})
fig.tight_layout()
fig.savefig(f"{FIG_DIR}/wykres2_cena_vs_powierzchnia.png", dpi=200)
plt.close(fig)
print(f"Korelacja Pearsona cena-powierzchnia (r): {r:.2f}")
print(f"Współczynnik determinacji (R²): {r**2:.2f}")
print(f"Korelacja Spearmana cena-powierzchnia (rho): {rho:.2f}")


# --- Wykres 3: top 5 miast wg liczby ofert ---
top5 = df["city_pl"].value_counts().head(5)

fig, ax = plt.subplots()
bars = ax.bar(top5.index, top5.values, color=COLOR)
for bar, value in zip(bars, top5.values):
    share = value / len(df) * 100
    ax.text(bar.get_x() + bar.get_width() / 2, value + 60,
            f"{spaced(value)}\n({comma(share, 1)}%)", ha="center", va="bottom", fontsize=11)
ax.set_title("Pięć miast z największą liczbą ofert")
ax.set_xlabel("Miasto")
ax.set_ylabel("Liczba ofert")
ax.set_ylim(0, top5.max() * 1.18)
ax.yaxis.set_major_formatter(FuncFormatter(spaced))
fig.tight_layout()
fig.savefig(f"{FIG_DIR}/wykres3_top5_miast.png", dpi=200)
plt.close(fig)
print(f"Udział 5 największych miast w ofertach [%]: {top5.sum() / len(df) * 100:.1f}")


# --- Wykres 4: mediana ceny za m² w miastach ---
med = df.groupby("city_pl")["price_per_sqm"].median().sort_values()
H, p_kw = stats.kruskal(*[g["price_per_sqm"].values for _, g in df.groupby("city")])

fig, ax = plt.subplots(figsize=(10, 7))
bars = ax.barh(med.index, med.values, color=COLOR)
for bar, value in zip(bars, med.values):
    ax.text(value + 150, bar.get_y() + bar.get_height() / 2,
            spaced(value), va="center", fontsize=10)
ax.set_title("Mediana ceny za m² w 15 największych miastach")
ax.set_xlabel("Mediana ceny za m² [zł]")
ax.set_ylabel("Miasto")
ax.set_xlim(0, med.max() * 1.12)
ax.xaxis.set_major_formatter(FuncFormatter(spaced))
ax.text(0.98, 0.04, f"Test Kruskala–Wallisa: H = {spaced(H)}, p < 0,001",
        transform=ax.transAxes, ha="right", fontsize=11,
        bbox={"boxstyle": "round", "facecolor": "white", "edgecolor": "gray"})
fig.tight_layout()
fig.savefig(f"{FIG_DIR}/wykres4_mediana_cena_za_m2_miasta.png", dpi=200)
plt.close(fig)
print(f"Statystyka testu Kruskala-Wallisa (H): {H:.0f}")
print(f"Wartość p testu Kruskala-Wallisa: {p_kw:.3g}")

print(f"Zapisano wykresy w folderze: {FIG_DIR}")
