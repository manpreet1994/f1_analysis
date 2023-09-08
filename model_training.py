from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd
import pickle

def save_pickle(model):
    with open('../data/fantasy_score_predictor.pkl', 'wb') as handle:
        pickle.dump(model, handle, protocol=pickle.HIGHEST_PROTOCOL)

def read_pickle():
    with open('../data/fantasy_score_predictor.pkl', 'rb') as handle:
        model = pickle.load(handle)
    return model

def binnning_scores(score):
    if score >= 25:
        return 2
    elif score >= 12:
        return 1
    else:
        return 0

def give_labels(category):
    if category == 0:
        return "below 12"
    elif category == 1:
        return "between 12 - 25"
    else:
        return "more than 25"

def train_model(training_df):
    train_data = training_df[(training_df.race_no != 12)]
    train_data = train_data.fillna(0)
    train_data['score_bin'] = train_data.score.apply(binnning_scores)
    X = train_data[['fp1', 'fp2', 'fp3', 'cost']]
    Y = train_data['score_bin']

    #create model
    model = XGBClassifier()
    model.fit(X, Y)

    save_pickle(model)
    return "Success"

def train():
    raw_data = pd.read_csv("../data/free_practice_metadata.csv")
    train_model(raw_data)

def predict(X_test):
    model = read_pickle()
    y_pred = model.predict(X_test[['fp1', 'fp2', 'fp3', 'cost']])

    return [give_labels(x) for x in y_pred]
