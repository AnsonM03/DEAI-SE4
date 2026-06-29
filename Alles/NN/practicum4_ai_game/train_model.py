import os
import csv
from pathlib import Path

import joblib
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "training_data.csv"
MODEL_DIR = PROJECT_ROOT / "models"
RESULT_DIR = PROJECT_ROOT / "results"
FEATURE_COLUMNS = [
    "car_x",
    "obstacle_x",
    "obstacle_y",
    "lane_delta",
    "obstacle_speed",
    "obstacle_type",
]
CSV_COLUMNS = FEATURE_COLUMNS + ["action"]
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

if not DATA_PATH.exists():
    raise FileNotFoundError("Geen training_data.csv gevonden. Speel eerst de game in human mode.")

def load_training_data(path):
    try:
        df = pd.read_csv(path).dropna()
    except pd.errors.ParserError:
        df = None

    if df is not None and all(column in df.columns for column in CSV_COLUMNS):
        return df[CSV_COLUMNS]

    recovered_rows = []
    skipped_rows = 0
    with open(path, newline="") as f:
        for row in csv.reader(f):
            if row == CSV_COLUMNS:
                continue
            if len(row) == len(CSV_COLUMNS):
                recovered_rows.append(row)
            else:
                skipped_rows += 1

    if not recovered_rows:
        raise ValueError(
            "De training_data.csv past niet bij het nieuwe autospel. "
            "Speel eerst game_collect_data.py om nieuwe auto-data te verzamelen."
        )

    print(
        f"Gemixte dataset gevonden: {len(recovered_rows)} autospel-regels gebruikt, "
        f"{skipped_rows} oude/ongeldige regels overgeslagen."
    )
    df = pd.DataFrame(recovered_rows, columns=CSV_COLUMNS)
    for column in CSV_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    return df.dropna()


df = load_training_data(DATA_PATH)
if df["action"].nunique() < 2:
    raise ValueError("Er zijn te weinig verschillende acties in de dataset. Verzamel meer rij-data.")

X = df[FEATURE_COLUMNS].values
y = df["action"].values

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
joblib.dump(scaler, MODEL_DIR / "scaler.joblib")

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.25, random_state=42, stratify=y)

classes, counts = np.unique(y_train, return_counts=True)
class_weight = {
    int(class_id): len(y_train) / (len(classes) * count)
    for class_id, count in zip(classes, counts)
}
print("Class weights:", class_weight)

base_experiments = [
    {"layers": [16], "epochs": 10, "lr": 0.001, "batch": 32},
    {"layers": [32], "epochs": 10, "lr": 0.001, "batch": 32},
    {"layers": [64], "epochs": 15, "lr": 0.001, "batch": 32},
    {"layers": [32, 16], "epochs": 15, "lr": 0.001, "batch": 32},
    {"layers": [64, 32], "epochs": 20, "lr": 0.001, "batch": 32},
    {"layers": [128, 64], "epochs": 20, "lr": 0.001, "batch": 64},
    {"layers": [32], "epochs": 20, "lr": 0.01, "batch": 32},
    {"layers": [32], "epochs": 20, "lr": 0.0001, "batch": 32},
    {"layers": [64, 32, 16], "epochs": 20, "lr": 0.001, "batch": 32},
    {"layers": [128, 64, 32], "epochs": 25, "lr": 0.001, "batch": 64},
]
experiments = []
for base in base_experiments:
    for epochs in [5, 10, 20]:
        copy = dict(base); copy["epochs"] = epochs; experiments.append(copy)
experiments = experiments[:30]

def build_model(layers, lr):
    model = tf.keras.Sequential([tf.keras.layers.Input(shape=(X_train.shape[1],))])
    for nodes in layers:
        model.add(tf.keras.layers.Dense(nodes, activation="relu"))
    model.add(tf.keras.layers.Dense(3, activation="softmax"))
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=lr), loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model

results = []
best_score = -1
best_model = None
for i, exp in enumerate(experiments, start=1):
    print(f"Experiment {i}/{len(experiments)}", exp)
    model = build_model(exp["layers"], exp["lr"])
    history = model.fit(
        X_train,
        y_train,
        validation_split=0.2,
        epochs=exp["epochs"],
        batch_size=exp["batch"],
        class_weight=class_weight,
        verbose=0,
    )
    y_pred = np.argmax(model.predict(X_test, verbose=0), axis=1)
    test_acc = accuracy_score(y_test, y_pred)
    weighted_f1 = f1_score(y_test, y_pred, average="weighted")
    macro_f1 = f1_score(y_test, y_pred, average="macro")
    row = {"experiment": i, "layers": str(exp["layers"]), "epochs": exp["epochs"], "learning_rate": exp["lr"], "batch_size": exp["batch"], "dataset_size": len(df), "train_accuracy": history.history["accuracy"][-1], "validation_accuracy": history.history["val_accuracy"][-1], "test_accuracy": test_acc, "weighted_f1_score": weighted_f1, "macro_f1_score": macro_f1}
    results.append(row)
    if macro_f1 > best_score:
        best_score = macro_f1; best_model = model

results_df = pd.DataFrame(results)
results_df.to_csv(RESULT_DIR / "experiment_results.csv", index=False)
results_df.to_excel(RESULT_DIR / "experiment_results.xlsx", index=False)
best_model.save(MODEL_DIR / "best_model.keras")
print("Beste macro F1:", best_score)
print(results_df.sort_values("macro_f1_score", ascending=False).head())
