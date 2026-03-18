import pandas as pd
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score


#SPLITTING DATA#
def load_and_split_data():
    df = pd.read_csv("data/prompts.csv")
    X = df["text"]
    Y = df["label"]

    X_train, X_test, Y_train, Y_test = train_test_split(
        X, Y, test_size=0.2, random_state=42, stratify=Y
    )

    return X_train, X_test, Y_train, Y_test

#VECTORIZE# 
def vectorize_data(X_train, X_test):
    vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=2) 
    X_train_vec = vectorizer.fit_transform(X_train) 
    X_test_vec = vectorizer.transform(X_test)

    print(X_train_vec)

    return vectorizer, X_train_vec, X_test_vec

##LOGISITIC REGRESSION##
def train_model(X_train_vec, Y_train):
    model = LogisticRegression()
    model.fit(X_train_vec, Y_train)
    return model

##PHASE 2##
def evaluate_model(Y_test, Y_pred):
    print("Accuracy:", accuracy_score(Y_test, Y_pred))
    print(classification_report(Y_test, Y_pred))
    print(confusion_matrix(Y_test, Y_pred))

def save_mistakes(X_test, Y_test, Y_pred):
    mistakes = []
    for text, true_label, pred_label in zip(X_test.tolist(), Y_test.tolist(), Y_pred):
        if true_label != pred_label:
            mistakes.append([text, true_label, pred_label])

    mistakes_df = pd.DataFrame(
        mistakes,
        columns=["Prompt", "True Label", "Predicted Label"]
    )
    mistakes_df.to_csv("model_mistakes.csv", index=False)

def save_model_vectorizer(model, vectorizer): 
        with open("ml/train_model.pkl", "wb") as file_model:
            pickle.dump(model, file_model)
        with open("ml/train_vectorizer.pkl", "wb") as file_vectorizer:
            pickle.dump(vectorizer, file_vectorizer)

def save_split_data(X_train, X_test, Y_train, Y_test):
    X_train.to_csv("train_features.csv", index=False)
    Y_train.to_csv("train_target.csv", index=False)
    X_test.to_csv("test_features.csv", index=False)
    Y_test.to_csv("test_target.csv", index=False)

def make_predictions(model, X_test_vec, X_test, Y_test):
    Y_pred = model.predict(X_test_vec)

    for prompt, true_label, pred_label in zip(X_test.tolist(), Y_test.tolist(), Y_pred):
        print("Prompt:", prompt)
        print("True Label:", true_label)
        print("Predicted Label:", pred_label)
        print("-----")

    return Y_pred

def main():
    X_train, X_test, Y_train, Y_test = load_and_split_data()
    save_split_data(X_train, X_test, Y_train, Y_test)

    vectorizer, X_train_vec, X_test_vec = vectorize_data(X_train, X_test)
    model = train_model(X_train_vec, Y_train)
    Y_pred = make_predictions(model, X_test_vec, X_test, Y_test)

    evaluate_model(Y_test, Y_pred)
    save_mistakes(X_test, Y_test, Y_pred)
    save_model_vectorizer(model, vectorizer)


if __name__ == "__main__":
    main()

