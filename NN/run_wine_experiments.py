from pathlib import Path
import random

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Dropout, Input
from tensorflow.keras.optimizers import Adam


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "experiment_results"
OUTPUT_DIR.mkdir(exist_ok=True)

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)
random.seed(RANDOM_STATE)
tf.random.set_seed(RANDOM_STATE)


def load_wine_data():
    red = pd.read_csv(BASE_DIR / "redwinequality.csv", sep=";")
    white = pd.read_csv(BASE_DIR / "whitewinequality.csv", sep=";")
    red["wine_type"] = 0
    white["wine_type"] = 1
    data = pd.concat([red, white], ignore_index=True)

    x = data.drop(columns=["quality"])
    y = (data["quality"] >= 6).astype(int)

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    x_test_scaled = scaler.transform(x_test)
    return x_train_scaled, x_test_scaled, y_train, y_test


def build_model(input_dim, hidden_layers, hidden_nodes, learning_rate, activation, dropout):
    model = Sequential()
    model.add(Input(shape=(input_dim,)))
    model.add(Dense(hidden_nodes, activation=activation))

    for _ in range(hidden_layers - 1):
        model.add(Dense(hidden_nodes, activation=activation))
        if dropout > 0:
            model.add(Dropout(dropout))

    model.add(Dense(1, activation="sigmoid"))
    model.compile(
        optimizer=Adam(learning_rate=learning_rate),
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )
    return model


def experiment_settings():
    return [
        {"hidden_layers": 1, "hidden_nodes": 8, "epochs": 20, "learning_rate": 0.001, "batch_size": 32, "activation": "relu", "dropout": 0.0},
        {"hidden_layers": 1, "hidden_nodes": 16, "epochs": 20, "learning_rate": 0.001, "batch_size": 32, "activation": "relu", "dropout": 0.0},
        {"hidden_layers": 1, "hidden_nodes": 32, "epochs": 20, "learning_rate": 0.001, "batch_size": 32, "activation": "relu", "dropout": 0.0},
        {"hidden_layers": 1, "hidden_nodes": 64, "epochs": 20, "learning_rate": 0.001, "batch_size": 32, "activation": "relu", "dropout": 0.0},
        {"hidden_layers": 2, "hidden_nodes": 16, "epochs": 20, "learning_rate": 0.001, "batch_size": 32, "activation": "relu", "dropout": 0.0},
        {"hidden_layers": 2, "hidden_nodes": 32, "epochs": 20, "learning_rate": 0.001, "batch_size": 32, "activation": "relu", "dropout": 0.0},
        {"hidden_layers": 2, "hidden_nodes": 64, "epochs": 20, "learning_rate": 0.001, "batch_size": 32, "activation": "relu", "dropout": 0.0},
        {"hidden_layers": 3, "hidden_nodes": 16, "epochs": 20, "learning_rate": 0.001, "batch_size": 32, "activation": "relu", "dropout": 0.0},
        {"hidden_layers": 3, "hidden_nodes": 32, "epochs": 20, "learning_rate": 0.001, "batch_size": 32, "activation": "relu", "dropout": 0.0},
        {"hidden_layers": 3, "hidden_nodes": 64, "epochs": 20, "learning_rate": 0.001, "batch_size": 32, "activation": "relu", "dropout": 0.0},
        {"hidden_layers": 2, "hidden_nodes": 32, "epochs": 10, "learning_rate": 0.001, "batch_size": 32, "activation": "relu", "dropout": 0.0},
        {"hidden_layers": 2, "hidden_nodes": 32, "epochs": 30, "learning_rate": 0.001, "batch_size": 32, "activation": "relu", "dropout": 0.0},
        {"hidden_layers": 2, "hidden_nodes": 32, "epochs": 50, "learning_rate": 0.001, "batch_size": 32, "activation": "relu", "dropout": 0.0},
        {"hidden_layers": 2, "hidden_nodes": 32, "epochs": 20, "learning_rate": 0.0005, "batch_size": 32, "activation": "relu", "dropout": 0.0},
        {"hidden_layers": 2, "hidden_nodes": 32, "epochs": 20, "learning_rate": 0.005, "batch_size": 32, "activation": "relu", "dropout": 0.0},
        {"hidden_layers": 2, "hidden_nodes": 32, "epochs": 20, "learning_rate": 0.01, "batch_size": 32, "activation": "relu", "dropout": 0.0},
        {"hidden_layers": 2, "hidden_nodes": 32, "epochs": 20, "learning_rate": 0.001, "batch_size": 16, "activation": "relu", "dropout": 0.0},
        {"hidden_layers": 2, "hidden_nodes": 32, "epochs": 20, "learning_rate": 0.001, "batch_size": 64, "activation": "relu", "dropout": 0.0},
        {"hidden_layers": 2, "hidden_nodes": 32, "epochs": 20, "learning_rate": 0.001, "batch_size": 128, "activation": "relu", "dropout": 0.0},
        {"hidden_layers": 2, "hidden_nodes": 32, "epochs": 20, "learning_rate": 0.001, "batch_size": 32, "activation": "tanh", "dropout": 0.0},
        {"hidden_layers": 2, "hidden_nodes": 64, "epochs": 20, "learning_rate": 0.001, "batch_size": 32, "activation": "tanh", "dropout": 0.0},
        {"hidden_layers": 3, "hidden_nodes": 32, "epochs": 30, "learning_rate": 0.001, "batch_size": 32, "activation": "tanh", "dropout": 0.0},
        {"hidden_layers": 2, "hidden_nodes": 32, "epochs": 20, "learning_rate": 0.001, "batch_size": 32, "activation": "relu", "dropout": 0.1},
        {"hidden_layers": 2, "hidden_nodes": 32, "epochs": 20, "learning_rate": 0.001, "batch_size": 32, "activation": "relu", "dropout": 0.2},
        {"hidden_layers": 3, "hidden_nodes": 64, "epochs": 30, "learning_rate": 0.001, "batch_size": 32, "activation": "relu", "dropout": 0.1},
        {"hidden_layers": 3, "hidden_nodes": 64, "epochs": 30, "learning_rate": 0.001, "batch_size": 32, "activation": "relu", "dropout": 0.2},
        {"hidden_layers": 4, "hidden_nodes": 32, "epochs": 30, "learning_rate": 0.001, "batch_size": 32, "activation": "relu", "dropout": 0.1},
        {"hidden_layers": 4, "hidden_nodes": 64, "epochs": 30, "learning_rate": 0.001, "batch_size": 32, "activation": "relu", "dropout": 0.1},
        {"hidden_layers": 2, "hidden_nodes": 128, "epochs": 30, "learning_rate": 0.001, "batch_size": 32, "activation": "relu", "dropout": 0.2},
        {"hidden_layers": 3, "hidden_nodes": 128, "epochs": 30, "learning_rate": 0.0005, "batch_size": 32, "activation": "relu", "dropout": 0.2},
    ]


def run_experiments():
    x_train, x_test, y_train, y_test = load_wine_data()
    results = []

    for experiment_id, params in enumerate(experiment_settings(), start=1):
        tf.keras.backend.clear_session()
        tf.random.set_seed(RANDOM_STATE + experiment_id)

        model = build_model(
            input_dim=x_train.shape[1],
            hidden_layers=params["hidden_layers"],
            hidden_nodes=params["hidden_nodes"],
            learning_rate=params["learning_rate"],
            activation=params["activation"],
            dropout=params["dropout"],
        )

        history = model.fit(
            x_train,
            y_train,
            validation_split=0.2,
            epochs=params["epochs"],
            batch_size=params["batch_size"],
            verbose=0,
        )

        probabilities = model.predict(x_test, verbose=0).ravel()
        predictions = (probabilities >= 0.5).astype(int)

        result = {
            "experiment_id": experiment_id,
            **params,
            "train_accuracy_last_epoch": history.history["accuracy"][-1],
            "validation_accuracy_last_epoch": history.history["val_accuracy"][-1],
            "test_accuracy": accuracy_score(y_test, predictions),
            "test_precision": precision_score(y_test, predictions, zero_division=0),
            "test_recall": recall_score(y_test, predictions, zero_division=0),
            "test_f1": f1_score(y_test, predictions, zero_division=0),
            "final_train_loss": history.history["loss"][-1],
            "final_validation_loss": history.history["val_loss"][-1],
        }
        results.append(result)
        print(
            f"Experiment {experiment_id:02d}: "
            f"accuracy={result['test_accuracy']:.4f}, "
            f"f1={result['test_f1']:.4f}"
        )

    results_df = pd.DataFrame(results).sort_values("test_accuracy", ascending=False)
    csv_path = OUTPUT_DIR / "wine_nn_experiment_results.csv"
    xlsx_path = OUTPUT_DIR / "wine_nn_experiment_results.xlsx"
    results_df.to_csv(csv_path, index=False)
    results_df.to_excel(xlsx_path, index=False)
    create_plots(results_df)
    return results_df


def create_plots(results_df):
    plt.style.use("seaborn-v0_8-whitegrid")

    top_results = results_df.sort_values("test_accuracy", ascending=False).head(15)
    labels = [f"Exp {int(row.experiment_id)}" for row in top_results.itertuples()]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(labels, top_results["test_accuracy"], color="#2f6f9f")
    ax.set_title("Top 15 experimenten op test accuracy")
    ax.set_xlabel("Experiment")
    ax.set_ylabel("Test accuracy")
    ax.set_ylim(0, 1)
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "top_15_test_accuracy.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(
        results_df["hidden_nodes"],
        results_df["test_accuracy"],
        c=results_df["hidden_layers"],
        s=results_df["epochs"] * 4,
        cmap="viridis",
        alpha=0.8,
        edgecolor="black",
        linewidth=0.5,
    )
    ax.set_title("Performance per aantal nodes, layers en epochs")
    ax.set_xlabel("Aantal hidden nodes")
    ax.set_ylabel("Test accuracy")
    ax.set_ylim(0, 1)
    colorbar = fig.colorbar(scatter, ax=ax)
    colorbar.set_label("Aantal hidden layers")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "nodes_layers_epochs_accuracy.png", dpi=150)
    plt.close(fig)

    metric_columns = ["test_accuracy", "test_precision", "test_recall", "test_f1"]
    top_10 = results_df.sort_values("test_accuracy", ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(top_10))
    width = 0.2
    for offset, metric in enumerate(metric_columns):
        ax.bar(x + (offset - 1.5) * width, top_10[metric], width, label=metric)
    ax.set_title("Vergelijking van metrics voor de top 10 experimenten")
    ax.set_xlabel("Experiment")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1)
    ax.set_xticks(x)
    ax.set_xticklabels([f"Exp {int(i)}" for i in top_10["experiment_id"]])
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "top_10_metric_comparison.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    results = run_experiments()
    print("\nBeste experiment:")
    print(results.head(1).to_string(index=False))
