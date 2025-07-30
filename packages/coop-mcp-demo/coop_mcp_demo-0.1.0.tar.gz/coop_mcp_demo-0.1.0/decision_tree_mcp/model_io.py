import joblib

def save_model(model, path='decision_tree_model.pkl'):
    joblib.dump(model, path)

def load_model(path='decision_tree_model.pkl'):
    return joblib.load(path)