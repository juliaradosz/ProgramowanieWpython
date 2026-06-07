"""Wizualizacje eksploracyjne i podsumowujące.

Zawiera m.in. chmury słów (wymagane jako przykład w treści projektu),
rozkład klas oraz zbiorcze porównanie skuteczności modeli.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud

from .evaluation import ModelResult


def plot_class_distribution(df: pd.DataFrame, out_path) -> None:
    """Słupkowy wykres liczności klas – pokazuje niezbalansowanie zbioru."""
    counts = df["label"].value_counts()
    fig, ax = plt.subplots(figsize=(5, 4))
    bars = ax.bar(
        counts.index, counts.values, color=["#4C72B0", "#C44E52"]
    )
    ax.bar_label(bars)
    ax.set_title("Rozkład klas w zbiorze (ham vs spam)")
    ax.set_ylabel("Liczba wiadomości")
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def plot_message_length(df: pd.DataFrame, out_path) -> None:
    """Histogram długości wiadomości w rozbiciu na klasy.

    Spam bywa systematycznie dłuższy – to przykład cechy odróżniającej klasy.
    """
    lengths = df.assign(length=df["message"].str.len())
    fig, ax = plt.subplots(figsize=(6, 4))
    for label, color in (("ham", "#4C72B0"), ("spam", "#C44E52")):
        subset = lengths.loc[lengths["label"] == label, "length"]
        ax.hist(subset, bins=40, alpha=0.6, label=label, color=color)
    ax.set_title("Rozkład długości wiadomości")
    ax.set_xlabel("Liczba znaków")
    ax.set_ylabel("Liczba wiadomości")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def plot_wordclouds(df: pd.DataFrame, out_path) -> None:
    """Dwie chmury słów: osobno dla wiadomości ham i spam."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, (label, title) in zip(
        axes, (("ham", "Ham (pożądane)"), ("spam", "Spam / phishing"))
    ):
        text = " ".join(df.loc[df["label"] == label, "message"].astype(str))
        cloud = WordCloud(
            width=800,
            height=500,
            background_color="white",
            colormap="viridis",
            max_words=120,
        ).generate(text)
        ax.imshow(cloud, interpolation="bilinear")
        ax.set_title(title, fontsize=14)
        ax.axis("off")
    fig.suptitle("Chmury słów – najczęstsze tokeny w klasach", fontsize=15)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def plot_model_comparison(results: list[ModelResult], out_path) -> None:
    """Zbiorczy wykres słupkowy: dokładność i F1 wszystkich modeli."""
    results_sorted = sorted(results, key=lambda r: r.f1, reverse=True)
    names = [r.name for r in results_sorted]
    acc = [r.accuracy for r in results_sorted]
    f1 = [r.f1 for r in results_sorted]

    x = range(len(names))
    width = 0.38
    fig, ax = plt.subplots(figsize=(10, 5))
    b1 = ax.bar([i - width / 2 for i in x], acc, width, label="Accuracy")
    b2 = ax.bar([i + width / 2 for i in x], f1, width, label="F1 (spam)")
    ax.bar_label(b1, fmt="%.3f", fontsize=8)
    ax.bar_label(b2, fmt="%.3f", fontsize=8)
    ax.set_xticks(list(x), labels=names, rotation=25, ha="right")
    ax.set_ylim(0.0, 1.05)
    ax.set_title("Porównanie skuteczności modeli (sortowane wg F1)")
    ax.set_ylabel("Wartość metryki")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
