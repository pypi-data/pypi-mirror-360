# model_io.py
def save_model(model, path='logistic_model.pkl'):
    import joblib
    joblib.dump(model, path)

def load_model(path='logistic_model.pkl'):
    import joblib
    return joblib.load(path)