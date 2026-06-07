"""Orkiestracja całego eksperymentu uczenia maszynowego.

Kolejność działań:
    1. wczytanie i oczyszczenie danych,
    2. wizualizacje eksploracyjne (rozkład klas, długości, chmury słów),
    3. pre-processing (czyszczenie tekstu + TF-IDF + podział),
    4. dla każdego modelu: strojenie hiperparametrów (GridSearchCV),
    5. ocena na zbiorze testowym + wykresy diagnostyczne,
    6. wybór najlepszego modelu wraz z uzasadnieniem,
    7. zapis najlepszego modelu i tabeli metryk.
"""

from __future__ import annotations

import joblib
import pandas as pd
from sklearn.model_selection import GridSearchCV

from . import config, evaluation, models, visualization
from .data_loader import load_dataframe
from .evaluation import ModelResult
from .preprocessing import prepare_dataset


def _run_eda(df: pd.DataFrame) -> None:
    """Generuje wykresy eksploracyjnej analizy danych (EDA)."""
    print("[pipeline] Generuję wizualizacje eksploracyjne...")
    visualization.plot_class_distribution(
        df, config.RESULTS_DIR / "01_rozklad_klas.png"
    )
    visualization.plot_message_length(
        df, config.RESULTS_DIR / "02_dlugosc_wiadomosci.png"
    )
    visualization.plot_wordclouds(
        df, config.RESULTS_DIR / "03_chmury_slow.png"
    )


def _select_best(results: list[ModelResult]) -> ModelResult:
    """Wybiera najlepszy model.

    Kryterium główne: **F1 dla klasy spam**, a nie sama dokładność. Przy
    ~13% udziale spamu klasyfikator zawsze przewidujący "ham" miałby ~87%
    dokładności, będąc bezużytecznym. F1 równoważy precyzję i czułość.
    Remis rozstrzyga wyższe ROC AUC.
    """
    return max(results, key=lambda r: (round(r.f1, 4), round(r.roc_auc, 4)))


def run() -> ModelResult:
    """Uruchamia pełny eksperyment i zwraca wynik najlepszego modelu."""
    config.ensure_dirs()

    # --- 1-2. Dane + EDA ----------------------------------------------------
    df = load_dataframe()
    _run_eda(df)

    # --- 3. Pre-processing --------------------------------------------------
    data = prepare_dataset(df)

    # --- 4-5. Trening, strojenie i ocena modeli -----------------------------
    zoo = models.get_model_zoo()
    results: list[ModelResult] = []
    fitted: dict = {}

    for name, (estimator, param_grid) in zoo.items():
        print(f"\n[pipeline] === Model: {name} ===")
        # GridSearchCV = eksperymenty z różnymi wartościami hiperparametrów
        # (5-krotna walidacja krzyżowa, optymalizacja pod F1).
        search = GridSearchCV(
            estimator,
            param_grid,
            scoring="f1",
            cv=5,
            n_jobs=-1,
        )
        search.fit(data.X_train_vec, data.y_train)
        best = search.best_estimator_
        print(f"[pipeline] Najlepsze hiperparametry: {search.best_params_}")

        result = evaluation.evaluate_model(
            name, best, search.best_params_, data.X_test_vec, data.y_test
        )
        results.append(result)
        fitted[name] = best

        slug = name.lower().replace(" ", "_").replace("(", "").replace(")", "")
        evaluation.plot_confusion_matrix(
            result, config.RESULTS_DIR / f"cm_{slug}.png"
        )
        evaluation.plot_learning_curve(
            name,
            best,
            data.X_train_vec,
            data.y_train,
            config.RESULTS_DIR / f"lc_{slug}.png",
        )

    # Krzywa straty sieci neuronowej (proces uczenia w epokach).
    evaluation.plot_mlp_loss_curve(
        fitted["Sieć neuronowa (MLP)"],
        config.RESULTS_DIR / "mlp_krzywa_straty.png",
    )

    # --- 6. Wykresy zbiorcze + wybór najlepszego modelu ---------------------
    evaluation.plot_roc_curves(
        fitted, data.X_test_vec, data.y_test,
        config.RESULTS_DIR / "04_krzywe_roc.png",
    )
    visualization.plot_model_comparison(
        results, config.RESULTS_DIR / "05_porownanie_modeli.png"
    )

    best_result = _select_best(results)

    # --- 7. Zapis wyników ---------------------------------------------------
    metrics_df = (
        pd.DataFrame(
            [
                {
                    "model": r.name,
                    "accuracy": r.accuracy,
                    "log_loss": r.loss,
                    "precision": r.precision,
                    "recall": r.recall,
                    "f1": r.f1,
                    "roc_auc": r.roc_auc,
                    "best_params": r.best_params,
                }
                for r in results
            ]
        )
        .sort_values("f1", ascending=False)
        .reset_index(drop=True)
    )
    metrics_df.to_csv(config.METRICS_FILE, index=False)

    # Zapisujemy najlepszy model RAZEM z wektoryzatorem (gotowy do predykcji).
    joblib.dump(
        {"model": fitted[best_result.name], "vectorizer": data.vectorizer},
        config.MODEL_FILE,
    )

    _print_summary(metrics_df, best_result)
    return best_result


def _print_summary(metrics_df: pd.DataFrame, best: ModelResult) -> None:
    """Wypisuje podsumowanie i uzasadnienie wyboru najlepszego modelu."""
    print("\n" + "=" * 70)
    print("PODSUMOWANIE – ranking modeli (wg F1 dla klasy spam):")
    print("=" * 70)
    print(metrics_df.drop(columns="best_params").to_string(index=False))
    print("\n" + "=" * 70)
    print(f"NAJLEPSZY MODEL: {best.name}")
    print("=" * 70)
    fn = int(best.confusion[1, 0])  # spam zaklasyfikowany jako ham
    fp = int(best.confusion[0, 1])  # ham zaklasyfikowany jako spam
    print(
        f"Uzasadnienie wyboru:\n"
        f"  * Najwyższe F1 = {best.f1:.4f} (a F1, nie accuracy, jest tu\n"
        f"    miarodajne, bo zbiór jest niezbalansowany – ~13% spamu).\n"
        f"  * ROC AUC = {best.roc_auc:.4f}, dokładność = {best.accuracy:.4f}.\n"
        f"  * Na zbiorze testowym: {fn} spamów przepuszczonych jako ham,\n"
        f"    {fp} poprawnych wiadomości błędnie oznaczonych jako spam.\n"
        f"  * Hiperparametry: {best.best_params}\n"
        f"\nModel + wektoryzator zapisano w: {config.MODEL_FILE}\n"
        f"Tabela metryk: {config.METRICS_FILE}\n"
        f"Wykresy: {config.RESULTS_DIR}"
    )
