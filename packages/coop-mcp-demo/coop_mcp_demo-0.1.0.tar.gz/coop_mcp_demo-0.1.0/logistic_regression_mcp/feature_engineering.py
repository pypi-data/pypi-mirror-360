# feature_engineering.py
def preprocess_features(df):
    from sklearn.preprocessing import LabelEncoder, StandardScaler
    categorical = ['job', 'marital', 'education', 'default', 'housing', 'loan', 'contact', 'month', 'poutcome']
    for col in categorical:
        df[col] = LabelEncoder().fit_transform(df[col])
    df['loan_income_ratio'] = df['balance'] / df['age']
    X = df.drop('y', axis=1)
    y = df['y']
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    return X_scaled, y