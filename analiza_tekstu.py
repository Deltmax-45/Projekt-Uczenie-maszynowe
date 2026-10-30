"""
Projekt 1 - Uczenie Maszynowe (Etap 1: Analiza danych)
Analiza tekstu zbioru 2 (Otodom, Warszawa, 15.05.2026): długość tekstów,
najczęstsze słowa, duplikaty i prawie-duplikaty, wykresy.

Uruchomienie (z katalogu głównego repozytorium):
    python analiza_tekstu.py
Wymaga pliku data/sample.parquet (oraz pakietu pyarrow). Wykresy trafiają do figures/.
"""

import collections
import itertools
import os
import re

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.ticker import FuncFormatter

DATA_PATH = "data/sample.parquet"
FIG_DIR = "figures"
TOP_N = 15                 # liczba najczęstszych słów
MIN_WORD_LEN = 3           # krótsze tokeny są pomijane
JACCARD_THRESHOLD = 0.8    # próg podobieństwa dla prawie-duplikatów
os.makedirs(FIG_DIR, exist_ok=True)

sns.set_theme(style="whitegrid")
plt.rcParams["axes.titlesize"] = 13
plt.rcParams["axes.labelsize"] = 11
COLOR = "#2f6db5"
COLOR_ACCENT = "#d1495b"

# Własna lista polskich słów funkcyjnych (stopwords)
STOPWORDS = set("""
aby albo ale ani bardzo bez bo choć czy czyli dla dość gdy gdyby gdyż gdzie go ich im jak jako jednak jego jej
jeśli jest jestem jeszcze już kiedy kilka która które który których którym którą lub mają mnie mogą może można
nad nam nas nasz nasze nawet nie nich niego niej nim około oraz pod ponad ponieważ poza przed przez przy raz
się są tak także tam tego tej ten też tuż tych tylko tym tutaj wiele więc wraz wszystkie wszystko wśród zaraz
zostanie żeby że było były był była będzie być każdy każda każde coś
""".split())

df_text = pd.read_parquet(DATA_PATH)
print(f"Liczba ogłoszeń w zbiorze 2: {df_text.shape[0]}")
print(f"Liczba kolumn w zbiorze 2: {df_text.shape[1]}")


def comma(value, digits=1):
    """Liczba z przecinkiem dziesiętnym (polski zapis)."""
    return f"{value:.{digits}f}".replace(".", ",")


def tokens(text):
    """Małe litery, same litery (z polskimi znakami), bez krótkich tokenów."""
    return [t for t in re.findall(r"[a-ząćęłńóśźż]+", text.lower()) if len(t) >= MIN_WORD_LEN]


# --- 1. Długość tekstów ---
for col in ["title", "shortDescription"]:
    chars = df_text[col].str.len()
    words = df_text[col].str.split().str.len()
    print(f"{col} - liczba znaków: średnia={chars.mean():.1f}, mediana={chars.median():.0f}, "
          f"min={chars.min()}, maks.={chars.max()}")
    print(f"{col} - liczba słów: średnia={words.mean():.1f}, mediana={words.median():.0f}, "
          f"min={words.min()}, maks.={words.max()}")
n_truncated = int(df_text["shortDescription"].str.endswith("...").sum())
print(f"Liczba opisów shortDescription zakończonych znakami '...' (obciętych): {n_truncated}")


# --- 2. Najczęstsze słowa (bez stopwords) ---
all_tokens = []
doc_freq = collections.Counter()
for title, desc in zip(df_text["title"], df_text["shortDescription"]):
    toks = [t for t in tokens(f"{title} {desc}") if t not in STOPWORDS]
    all_tokens += toks
    doc_freq.update(set(toks))
counts = collections.Counter(all_tokens)
top_words = counts.most_common(TOP_N)
print(f"Liczba wszystkich słów po usunięciu stopwords: {len(all_tokens)}")
print(f"Liczba różnych słów po usunięciu stopwords: {len(counts)}")
print(f"Najczęstsze słowa (słowo: wystąpienia / liczba ogłoszeń zawierających słowo), top {TOP_N}:")
for word, c in top_words:
    print(f"  {word}: {c} / {doc_freq[word]}")


# --- 3. Duplikaty i prawie-duplikaty ---
dup_title_groups = int((df_text["title"].value_counts() > 1).sum())
dup_title_rows = int(df_text["title"].duplicated(keep=False).sum())
dup_desc_groups = int((df_text["shortDescription"].value_counts() > 1).sum())
dup_desc_rows = int(df_text["shortDescription"].duplicated(keep=False).sum())
dup_url_rows = int(df_text["detailUrl"].duplicated(keep=False).sum())
print(f"Identyczne tytuły: {dup_title_groups} grup, {dup_title_rows} ogłoszeń")
print(f"Identyczne opisy shortDescription: {dup_desc_groups} grup, {dup_desc_rows} ogłoszeń")
print(f"Ogłoszenia z powtórzonym adresem detailUrl: {dup_url_rows}")

title_sets = [set(tokens(t)) for t in df_text["title"]]
desc_sets = [set(tokens(d)) for d in df_text["shortDescription"]]


def jaccard(a, b):
    return len(a & b) / len(a | b) if (a | b) else 0.0


parent = list(range(len(df_text)))


def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


for i, j in itertools.combinations(range(len(df_text)), 2):
    if (jaccard(desc_sets[i], desc_sets[j]) >= JACCARD_THRESHOLD
            or jaccard(title_sets[i], title_sets[j]) >= JACCARD_THRESHOLD):
        parent[find(i)] = find(j)

groups = collections.defaultdict(list)
for i in range(len(df_text)):
    groups[find(i)].append(i)
clusters = sorted((g for g in groups.values() if len(g) > 1), key=len, reverse=True)
rows_in_clusters = sum(len(g) for g in clusters)
redundant = sum(len(g) - 1 for g in clusters)
print(f"Prawie-duplikaty (Jaccard >= {JACCARD_THRESHOLD}): {len(clusters)} grup, "
      f"{rows_in_clusters} ogłoszeń w grupach")
print(f"Liczba ogłoszeń po usunięciu nadmiarowych kopii: {len(df_text) - redundant}")
print(f"Rozmiary grup prawie-duplikatów: {[len(g) for g in clusters]}")
for g in clusters:
    print(f"  grupa {len(g)} ogłoszeń, przykładowy tytuł: {df_text['title'].iloc[g[0]][:70]}")
hala = df_text["title"].str.contains("Hala", case=False)
print(f"Ogłoszenia z frazą 'Hala' w tytule: {int(hala.sum())}, "
      f"liczba różnych agencji: {df_text.loc[hala, 'agencyName'].nunique()}")


# --- Wykres 5: długość tekstów ---
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
t_len = df_text["title"].str.len()
d_len = df_text["shortDescription"].str.len()

sns.histplot(t_len, bins=range(20, 76, 5), color=COLOR, ax=axes[0])
axes[0].axvline(t_len.median(), color=COLOR_ACCENT, linestyle="--", linewidth=2,
                label=f"Mediana: {t_len.median():.0f} znaków")
axes[0].set_title("Długość tytułu ogłoszenia")
axes[0].set_xlabel("Liczba znaków")
axes[0].set_ylabel("Liczba ogłoszeń")
axes[0].legend()

sns.histplot(d_len, discrete=True, color=COLOR, ax=axes[1])
axes[1].axvline(d_len.median(), color=COLOR_ACCENT, linestyle="--", linewidth=2,
                label=f"Mediana: {d_len.median():.0f} znaków")
axes[1].set_title("Długość shortDescription (opis obcięty do ok. 200 znaków)")
axes[1].set_xlabel("Liczba znaków")
axes[1].set_ylabel("Liczba ogłoszeń")
axes[1].legend(loc="upper left")

fig.suptitle("Zbiór 2 – długość tekstów (100 ogłoszeń, Warszawa)", fontsize=14)
fig.tight_layout()
fig.savefig(f"{FIG_DIR}/wykres5_dlugosc_tekstow.png", dpi=200)
plt.close(fig)


# --- Wykres 6: najczęstsze słowa ---
words_sorted = top_words[::-1]
fig, ax = plt.subplots(figsize=(10, 6.5))
bars = ax.barh([w for w, _ in words_sorted], [c for _, c in words_sorted], color=COLOR)
for bar, (word, c) in zip(bars, words_sorted):
    ax.text(c + 0.6, bar.get_y() + bar.get_height() / 2,
            f"{c} (w {doc_freq[word]} ogł.)", va="center", fontsize=9)
ax.set_title(f"Zbiór 2 – {TOP_N} najczęstszych słów w tytułach i opisach (bez stopwords)")
ax.set_xlabel("Liczba wystąpień")
ax.set_ylabel("Słowo")
ax.set_xlim(0, max(c for _, c in top_words) * 1.22)
ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _p: f"{x:.0f}"))
fig.tight_layout()
fig.savefig(f"{FIG_DIR}/wykres6_najczestsze_slowa.png", dpi=200)
plt.close(fig)

print(f"Zapisano wykresy w folderze: {FIG_DIR}")
