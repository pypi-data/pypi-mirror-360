import pandas as pd
import random


def sample_from_df(df, size=1):
    labels = []
    probabilities = []

    for idx_name in df.index:
        for col_name in df.columns:
            prob = df.loc[idx_name, col_name]
            if prob > 0:
                labels.append((idx_name, col_name))
                probabilities.append(prob)

    if not labels:
        return None, None, None

    mapping = {label: i for i, label in enumerate(labels)}

    chosen_labels = random.choices(labels, weights=probabilities, k=size)

    label_ids = [mapping[label] for label in chosen_labels]

    return chosen_labels, label_ids, mapping