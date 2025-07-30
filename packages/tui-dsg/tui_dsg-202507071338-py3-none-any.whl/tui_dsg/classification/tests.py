import numpy as np
import pandas as pd
from checkmarkandcross import image
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import precision_score, recall_score


def aufgabe1(df: pd.DataFrame, df_train: pd.DataFrame, df_test: pd.DataFrame):
    return image(isinstance(df, pd.DataFrame)
                 and isinstance(df_train, pd.DataFrame)
                 and isinstance(df_test, pd.DataFrame)
                 and len(df) == 1009
                 and 2.9 < len(df_train) / len(df_test) < 3.1)


def aufgabe2(nn: KNeighborsClassifier, nn_accuracy: float):
    return image(isinstance(nn, KNeighborsClassifier)
                 and isinstance(nn_accuracy, float) and 0.67 < nn_accuracy < 1)


def aufgabe3(tree: DecisionTreeClassifier, tree_accuracy: float):
    return image(isinstance(tree, DecisionTreeClassifier)
                 and isinstance(tree_accuracy, float) and 0.5 < tree_accuracy < 1)


def aufgabe4(nn: KNeighborsClassifier, nn_prediction: np.ndarray,
             tree: DecisionTreeClassifier, tree_prediction: np.ndarray):
    df_new = pd.DataFrame({'budget': 14145774,
                           'countries': 2,
                           'runtime': 109,
                           'cast_size': 38,
                           'crew_size': 136,
                           'cast_vote_avg': 6.8}, index=[0])

    return image(isinstance(nn, KNeighborsClassifier)
                 and isinstance(nn_prediction, np.ndarray)
                 and (nn_prediction == nn.predict(df_new)).all()
                 and isinstance(tree, DecisionTreeClassifier)
                 and isinstance(tree_prediction, np.ndarray)
                 and (tree_prediction == tree.predict(df_new)).all())


def aufgabe5(df: pd.DataFrame,
             nn: KNeighborsClassifier, nn_precision: float, nn_recall: float,
             tree: DecisionTreeClassifier, tree_precision: float, tree_recall: float):
    if not isinstance(df, pd.DataFrame):
        return image(False)

    # nn
    if not isinstance(nn, KNeighborsClassifier):
        return image(False)

    if not isinstance(nn_precision, float) or not isinstance(nn_recall, float):
        return image(False)

    true_nn_precision = precision_score(df['popular'], nn.predict(df.drop('popular', axis=1)))
    if abs(nn_precision - true_nn_precision) > 1e-6:
        return image(False)

    true_nn_recall = recall_score(df['popular'], nn.predict(df.drop('popular', axis=1)))
    if abs(nn_recall - true_nn_recall) > 1e-6:
        return image(False)

    # tree
    if not isinstance(tree, DecisionTreeClassifier):
        return image(False)

    if not isinstance(tree_precision, float) or not isinstance(tree_recall, float):
        return image(False)

    true_tree_precision = precision_score(df['popular'], tree.predict(df.drop('popular', axis=1)))
    if abs(tree_precision - true_tree_precision) > 1e-6:
        return image(False)

    true_tree_recall = recall_score(df['popular'], tree.predict(df.drop('popular', axis=1)))
    if abs(tree_recall - true_tree_recall) > 1e-6:
        return image(False)

    return image(True)
