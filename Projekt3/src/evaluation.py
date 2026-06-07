"""Ocena skuteczności modeli i wykresy diagnostyczne.

Realizuje wymagane metryki:
    * test accuracy        – dokładność na zbiorze testowym,
    * test loss            – logarytmiczna funkcja straty (log loss),
    * macierz błędów       – confusion matrix,
    * krzywe uczenia się   – learning curves (sklearn.learning_curve).

Dodatkowo, ze względu na NIEZBALANSOWANIE zbioru (~13% spamu), liczone są
precyzja, czułość, F1 oraz pole pod krzywą ROC (ROC AUC) – dla takich
danych sama dokładność bywa myląca.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import matplotlib

matplotlib.use("Agg")  # backend bezokienkowy – zapis wykresów do plików
import matplotlib.pyplot as plt
import numpy as np
from sklearn.base import ClassifierMixin
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import learning_curve

from . import config
from .preprocessing import LABEL_NAMES


@dataclass
class ModelResult:
    """Komplet metryk pojedynczego (najlepszego po strojeniu) modelu."""

    name: str
    best_params: dict
    accuracy: float
    loss: float
    precision: float
    recall: float
    f1: float
    roc_auc: float
    confusion: np.ndarray = field(repr=False)


def evaluate_model(
    name: str,
    model: ClassifierMixin,
    best_params: dict,
    X_test,
    y_test: np.ndarray,
) -> ModelResult:
    """Liczy wszystkie metryki dla wytrenowanego modelu na zbiorze testowym."""
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)

    result = ModelResult(
        name=name,
        best_params=best_params,
        accuracy=accuracy_score(y_test, y_pred),
        # log_loss z jawnym wykazem klas – odporne na brak klasy w predykcji.
        loss=log_loss(y_test, y_proba, labels=[0, 1]),
        precision=precision_score(y_test, y_pred, zero_division=0),
        recall=recall_score(y_test, y_pred, zero_division=0),
        f1=f1_score(y_test, y_pred, zero_division=0),
        roc_auc=roc_auc_score(y_test, y_proba[:, 1]),
        confusion=confusion_matrix(y_test, y_pred),
    )
    print(
        f"[eval] {name:24s} acc={result.accuracy:.4f} "
        f"loss={result.loss:.4f} F1={result.f1:.4f} "
        f"ROC-AUC={result.roc_auc:.4f}"
    )
    return result


def plot_confusion_matrix(result: ModelResult, out_path) -> None:
    """Rysuje i zapisuje macierz błędów jednego modelu."""
    cm = result.confusion
    fig, ax = plt.subplots(figsize=(4.5, 4))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_title(f"Macierz błędów – {result.name}")
    ax.set_xlabel("Predykcja")
    ax.set_ylabel("Prawdziwa klasa")
    ax.set_xticks([0, 1], labels=LABEL_NAMES, rotation=15)
    ax.set_yticks([0, 1], labels=LABEL_NAMES)
    thresh = cm.max() / 2.0
    for i in range(2):
        for j in range(2):
            ax.text(
                j,
                i,
                str(cm[i, j]),
                ha="center",
                va="center",
                color="white" if cm[i, j] > thresh else "black",
                fontsize=13,
            )
    fig.colorbar(im, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def plot_learning_curve(
    name: str, model: ClassifierMixin, X, y: np.ndarray, out_path
) -> None:
    """Rysuje krzywą uczenia się: skuteczność vs. liczba próbek treningowych.

    Rozjazd między krzywą treningową a walidacyjną wskazuje na przeuczenie;
    ich zbieżność na niskim poziomie – na niedouczenie.
    """
    train_sizes, train_scores, val_scores = learning_curve(
        model,
        X,
        y,
        cv=5,
        scoring="f1",
        train_sizes=np.linspace(0.1, 1.0, 6),
        random_state=config.RANDOM_STATE,
        n_jobs=-1,
    )
    train_mean = train_scores.mean(axis=1)
    val_mean = val_scores.mean(axis=1)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(train_sizes, train_mean, "o-", label="zbiór treningowy")
    ax.plot(train_sizes, val_mean, "s-", label="walidacja krzyżowa")
    ax.fill_between(
        train_sizes,
        train_scores.min(axis=1),
        train_scores.max(axis=1),
        alpha=0.12,
    )
    ax.fill_between(
        train_sizes,
        val_scores.min(axis=1),
        val_scores.max(axis=1),
        alpha=0.12,
    )
    ax.set_title(f"Krzywa uczenia się – {name}")
    ax.set_xlabel("Liczba próbek treningowych")
    ax.set_ylabel("F1 (klasa: spam)")
    ax.legend(loc="lower right")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def plot_roc_curves(
    fitted: dict[str, ClassifierMixin], X_test, y_test: np.ndarray, out_path
) -> None:
    """Rysuje krzywe ROC wszystkich modeli na jednym wykresie."""
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    for name, model in fitted.items():
        proba = model.predict_proba(X_test)[:, 1]
        fpr, tpr, _ = roc_curve(y_test, proba)
        auc = roc_auc_score(y_test, proba)
        ax.plot(fpr, tpr, label=f"{name} (AUC={auc:.3f})")
    ax.plot([0, 1], [0, 1], "k--", alpha=0.5, label="klasyfikator losowy")
    ax.set_title("Krzywe ROC – porównanie modeli")
    ax.set_xlabel("Odsetek fałszywie pozytywnych (FPR)")
    ax.set_ylabel("Odsetek prawdziwie pozytywnych (TPR)")
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def plot_mlp_loss_curve(model: ClassifierMixin, out_path) -> None:
    """Rysuje krzywą funkcji straty sieci neuronowej w kolejnych iteracjach.

    Dotyczy modelu MLP, który podczas uczenia minimalizuje funkcję straty
    (logarytmiczną) – jej spadek obrazuje proces uczenia sieci.
    """
    loss_curve = getattr(model, "loss_curve_", None)
    if not loss_curve:
        return
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(range(1, len(loss_curve) + 1), loss_curve, "o-", color="crimson")
    ax.set_title("Sieć neuronowa (MLP) – krzywa funkcji straty")
    ax.set_xlabel("Iteracja (epoka)")
    ax.set_ylabel("Funkcja straty (log loss)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
