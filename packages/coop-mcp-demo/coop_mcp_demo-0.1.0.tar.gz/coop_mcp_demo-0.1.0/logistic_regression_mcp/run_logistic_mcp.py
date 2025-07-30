# run_logistic_mcp.py
if __name__ == '__main__':
    from data_loader import load_data
    from feature_engineering import preprocess_features
    from resampling import balance_data
    from train_model import train_logistic
    from evaluate import evaluate_model
    from model_io import save_model, load_model
    from sklearn.model_selection import train_test_split
    df = load_data('C:/Users/admin/Documents/bank credit/data/bank.csv')
    X, y = preprocess_features(df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    X_train_resampled, y_train_resampled = balance_data(X_train, y_train)
    model = train_logistic(X_train_resampled, y_train_resampled)
    evaluate_model(model, X_test, y_test)
    save_model(model)
    print("Loaded prediction:", load_model().predict(X_test))
