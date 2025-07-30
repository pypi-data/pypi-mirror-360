import joblib

def save_model(model, path='random_forest_model.pkl'):
    joblib.dump(model, path)

def load_model(path='random_forest_model.pkl'):
    return joblib.load(path)