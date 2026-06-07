"""Definicje modeli uczenia maszynowego i siatek hiperparametrów.

Projekt realizuje wymóg "min. 5 modeli, które znacznie się różnią ORAZ
obejmują eksperymenty z różnymi wartościami parametrów". Zdefiniowano
7 modeli z 7 różnych rodzin algorytmów; dla każdego określono niewielką
siatkę hiperparametrów przeszukiwaną walidacją krzyżową (GridSearchCV).

Krótkie uzasadnienie doboru (różne paradygmaty uczenia):

    * Multinomial Naive Bayes  – model probabilistyczny, klasyczny baseline
      dla klasyfikacji tekstu; hiperparametr ``alpha`` to wygładzanie Laplace'a.
    * Regresja logistyczna     – model liniowy; ``C`` reguluje siłę regularyzacji.
    * k-Najbliższych Sąsiadów  – model leniwy/instancyjny; kluczowe ``k``
      (liczba sąsiadów) – wprost wymagany w treści projektu przykład.
    * Drzewo decyzyjne         – model regułowy; ``max_depth`` kontroluje
      złożoność i ryzyko przeuczenia.
    * Las losowy               – zespół drzew (bagging); uśrednia wiele drzew.
    * Maszyna wektorów nośnych – klasyfikator marginesowy (jądro liniowe).
    * Sieć neuronowa (MLP)     – wielowarstwowy perceptron; istotne są
      funkcja aktywacji i krzywa funkcji straty podczas uczenia.
"""

from __future__ import annotations

from sklearn.base import ClassifierMixin
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from . import config


def get_model_zoo() -> dict[str, tuple[ClassifierMixin, dict]]:
    """Zwraca słownik: nazwa -> (estymator, siatka hiperparametrów).

    Każda siatka jest celowo niewielka, aby pełny eksperyment był szybki,
    a jednocześnie pokazywał wpływ hiperparametrów na skuteczność.

    Wszystkie modele wspierają ``predict_proba``, co umożliwia policzenie
    ``test loss`` (logarytmiczna funkcja straty) oraz krzywych ROC.
    """
    rs = config.RANDOM_STATE
    return {
        "Naive Bayes": (
            MultinomialNB(),
            {"alpha": [0.1, 0.5, 1.0]},
        ),
        "Regresja logistyczna": (
            LogisticRegression(max_iter=1000, class_weight="balanced"),
            {"C": [0.1, 1.0, 10.0]},
        ),
        "k-NN": (
            KNeighborsClassifier(metric="cosine"),
            {"n_neighbors": [3, 5, 11]},
        ),
        "Drzewo decyzyjne": (
            DecisionTreeClassifier(
                class_weight="balanced", random_state=rs
            ),
            {"max_depth": [10, 30, None]},
        ),
        "Las losowy": (
            RandomForestClassifier(
                class_weight="balanced", random_state=rs, n_jobs=-1
            ),
            {"n_estimators": [100, 300], "max_depth": [None, 30]},
        ),
        "SVM (jądro liniowe)": (
            SVC(
                kernel="linear",
                probability=True,
                class_weight="balanced",
                random_state=rs,
            ),
            {"C": [0.5, 1.0, 5.0]},
        ),
        "Sieć neuronowa (MLP)": (
            MLPClassifier(
                hidden_layer_sizes=(64,),
                activation="relu",
                early_stopping=True,
                max_iter=200,
                random_state=rs,
            ),
            {"alpha": [1e-4, 1e-3], "hidden_layer_sizes": [(64,), (128, 32)]},
        ),
    }
