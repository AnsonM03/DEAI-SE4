from __future__ import annotations

import json
import time
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.exceptions import ConvergenceWarning
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


RANDOM_STATE = 42
DATA_FILE = Path(__file__).with_name("AmesHousing.xlsx")
OUTPUT_DIR = Path(__file__).with_name("ames_nn_results")
TARGET = "SalePrice"


FEATURE_SETS = {
    "lr_basis": ["Overall Qual", "Gr Liv Area", "Neighborhood"],
    "lr_uitgebreid": [
        "Overall Qual",
        "Gr Liv Area",
        "Total Bsmt SF",
        "Year Built",
        "Neighborhood",
    ],
    "lr_met_housestyle": [
        "Overall Qual",
        "Gr Liv Area",
        "Neighborhood",
        "House Style",
    ],
    "numeriek_alles": [
        "Overall Qual",
        "Gr Liv Area",
        "Total Bsmt SF",
        "Lot Area",
        "Year Built",
        "Full Bath",
        "Bedroom AbvGr",
    ],
    "sterke_subset": [
        "Overall Qual",
        "Gr Liv Area",
        "Total Bsmt SF",
        "Year Built",
        "Full Bath",
        "Neighborhood",
    ],
    "alle_features_zonder_id": [
        "Garage",
        "Overall Qual",
        "Gr Liv Area",
        "Total Bsmt SF",
        "Lot Area",
        "Year Built",
        "Full Bath",
        "Bedroom AbvGr",
        "Neighborhood",
        "House Style",
    ],
}


ARCHITECTURES = {
    "1x32": (32,),
    "1x64": (64,),
    "2x64_32": (64, 32),
    "2x128_64": (128, 64),
    "3x128_64_32": (128, 64, 32),
}

LEARNING_RATES = [0.01, 0.001, 0.0003]
EPOCHS = [300, 800]
VALIDATION_SIZES = [0.15, 0.20, 0.30]


def rmse(y_true, y_pred) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def metrics(y_true, y_pred) -> dict[str, float]:
    return {
        "r2": float(r2_score(y_true, y_pred)),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": rmse(y_true, y_pred),
    }


def build_preprocessor(x: pd.DataFrame) -> ColumnTransformer:
    numeric_features = x.select_dtypes(include=["number", "bool"]).columns.tolist()
    categorical_features = [c for c in x.columns if c not in numeric_features]

    numeric_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipe, numeric_features),
            ("cat", categorical_pipe, categorical_features),
        ],
        remainder="drop",
    )


def build_model(x: pd.DataFrame, estimator) -> TransformedTargetRegressor:
    pipeline = Pipeline(
        steps=[
            ("preprocess", build_preprocessor(x)),
            ("model", estimator),
        ]
    )
    return TransformedTargetRegressor(
        regressor=pipeline,
        transformer=StandardScaler(),
    )


def load_data() -> pd.DataFrame:
    df = pd.read_excel(DATA_FILE, sheet_name="AmesHousing")
    return df.drop(columns=["ID"], errors="ignore")


def evaluate_linear_baselines(df: pd.DataFrame, test_index: pd.Index) -> pd.DataFrame:
    rows = []
    for feature_set, features in FEATURE_SETS.items():
        data = df[[*features, TARGET]].copy()
        train_val = data.drop(index=test_index)
        test = data.loc[test_index]

        model = build_model(
            train_val[features],
            LinearRegression(),
        )
        model.fit(train_val[features], train_val[TARGET])
        pred = model.predict(test[features])
        row = {
            "model_type": "LinearRegression",
            "feature_set": feature_set,
            "features": ", ".join(features),
            "n_features_before_encoding": len(features),
            "validation_size": np.nan,
            "architecture": "-",
            "hidden_layers": 0,
            "learning_rate": np.nan,
            "epochs": np.nan,
            "train_seconds": np.nan,
        }
        row.update({f"test_{k}": v for k, v in metrics(test[TARGET], pred).items()})
        rows.append(row)
    return pd.DataFrame(rows)


def run_nn_experiments(df: pd.DataFrame, test_index: pd.Index) -> pd.DataFrame:
    train_val_df = df.drop(index=test_index)
    test_df = df.loc[test_index]
    rows = []
    total = (
        len(FEATURE_SETS)
        * len(VALIDATION_SIZES)
        * len(ARCHITECTURES)
        * len(LEARNING_RATES)
        * len(EPOCHS)
    )
    done = 0

    warnings.filterwarnings("ignore", category=ConvergenceWarning)

    for feature_set, features in FEATURE_SETS.items():
        base = train_val_df[[*features, TARGET]].copy()
        for validation_size in VALIDATION_SIZES:
            train_df, val_df = train_test_split(
                base,
                test_size=validation_size,
                random_state=RANDOM_STATE,
            )

            for architecture_name, hidden_layer_sizes in ARCHITECTURES.items():
                for learning_rate in LEARNING_RATES:
                    for epochs in EPOCHS:
                        done += 1
                        estimator = MLPRegressor(
                            hidden_layer_sizes=hidden_layer_sizes,
                            activation="relu",
                            solver="adam",
                            alpha=0.0001,
                            batch_size=32,
                            learning_rate_init=learning_rate,
                            max_iter=epochs,
                            random_state=RANDOM_STATE,
                            early_stopping=False,
                        )
                        model = build_model(train_df[features], estimator)
                        start = time.perf_counter()
                        model.fit(train_df[features], train_df[TARGET])
                        train_seconds = time.perf_counter() - start

                        val_pred = model.predict(val_df[features])
                        test_pred = model.predict(test_df[features])
                        row = {
                            "model_type": "NeuralNetwork_MLP",
                            "feature_set": feature_set,
                            "features": ", ".join(features),
                            "n_features_before_encoding": len(features),
                            "validation_size": validation_size,
                            "architecture": architecture_name,
                            "hidden_layers": len(hidden_layer_sizes),
                            "hidden_nodes": str(hidden_layer_sizes),
                            "learning_rate": learning_rate,
                            "epochs": epochs,
                            "train_rows": len(train_df),
                            "validation_rows": len(val_df),
                            "test_rows": len(test_df),
                            "train_seconds": train_seconds,
                        }
                        row.update(
                            {f"validation_{k}": v for k, v in metrics(val_df[TARGET], val_pred).items()}
                        )
                        row.update({f"test_{k}": v for k, v in metrics(test_df[TARGET], test_pred).items()})
                        rows.append(row)

                        if done % 25 == 0 or done == total:
                            print(f"{done}/{total} experimenten klaar")

    return pd.DataFrame(rows)


def make_plots(nn_results: pd.DataFrame, best_per_feature: pd.DataFrame) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    top_20 = nn_results.sort_values("validation_rmse").head(20).iloc[::-1]
    plt.figure(figsize=(12, 8))
    labels = (
        top_20["feature_set"]
        + " | "
        + top_20["architecture"]
        + " | lr="
        + top_20["learning_rate"].astype(str)
        + " | ep="
        + top_20["epochs"].astype(int).astype(str)
    )
    plt.barh(labels, top_20["validation_rmse"], color="#2f6f73")
    plt.xlabel("Validation RMSE")
    plt.title("Top 20 neural-network experimenten")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "top_20_nn_validation_rmse.png", dpi=160)
    plt.close()

    plt.figure(figsize=(10, 5))
    ordered = best_per_feature.sort_values("validation_rmse")
    plt.bar(ordered["feature_set"], ordered["validation_rmse"], color="#7a4f9a")
    plt.ylabel("Beste validation RMSE")
    plt.title("Beste neural network per feature set")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "best_feature_sets_validation_rmse.png", dpi=160)
    plt.close()


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    df = load_data()

    _, test_df = train_test_split(
        df,
        test_size=0.20,
        random_state=RANDOM_STATE,
    )
    test_index = test_df.index

    linear_results = evaluate_linear_baselines(df, test_index)
    nn_results = run_nn_experiments(df, test_index)

    best_per_feature = (
        nn_results.sort_values("validation_rmse")
        .groupby("feature_set", as_index=False)
        .first()
        .sort_values("validation_rmse")
    )
    best_overall = nn_results.sort_values("validation_rmse").iloc[0].to_dict()

    all_results = pd.concat([linear_results, nn_results], ignore_index=True, sort=False)
    comparison = best_per_feature[
        [
            "feature_set",
            "features",
            "validation_rmse",
            "validation_mae",
            "validation_r2",
            "test_rmse",
            "test_mae",
            "test_r2",
            "architecture",
            "learning_rate",
            "epochs",
            "validation_size",
        ]
    ].merge(
        linear_results[["feature_set", "test_rmse", "test_mae", "test_r2"]],
        on="feature_set",
        suffixes=("_nn", "_linear"),
    )
    comparison["rmse_verschil_nn_min_linear"] = (
        comparison["test_rmse_nn"] - comparison["test_rmse_linear"]
    )

    all_results.to_csv(OUTPUT_DIR / "ames_all_experiment_results.csv", index=False)
    nn_results.to_csv(OUTPUT_DIR / "ames_nn_experiment_results.csv", index=False)
    comparison.to_csv(OUTPUT_DIR / "ames_nn_vs_linear_comparison.csv", index=False)
    with pd.ExcelWriter(OUTPUT_DIR / "ames_nn_experiment_results.xlsx") as writer:
        nn_results.to_excel(writer, sheet_name="nn_all", index=False)
        linear_results.to_excel(writer, sheet_name="linear_baselines", index=False)
        comparison.to_excel(writer, sheet_name="comparison", index=False)
        best_per_feature.to_excel(writer, sheet_name="best_per_feature", index=False)

    make_plots(nn_results, best_per_feature)

    summary = {
        "dataset_shape": df.shape,
        "test_size": len(test_index),
        "nn_experiments": len(nn_results),
        "best_overall": best_overall,
        "best_feature_set_ranking": comparison.to_dict(orient="records"),
    }
    (OUTPUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("\nBeste NN-configuratie op basis van validation RMSE:")
    print(pd.Series(best_overall))
    print("\nVergelijking beste NN per feature set met lineaire regressie:")
    print(comparison.sort_values("validation_rmse").to_string(index=False))


if __name__ == "__main__":
    main()
