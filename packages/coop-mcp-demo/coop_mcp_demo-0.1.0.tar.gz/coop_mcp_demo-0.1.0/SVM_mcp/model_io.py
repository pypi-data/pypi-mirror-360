import joblib
def save_model(model, path='svm_model.pkl'):
    joblib.dump(model, path)

def load_model(path='svm_model.pkl'):
    return joblib.load(path)