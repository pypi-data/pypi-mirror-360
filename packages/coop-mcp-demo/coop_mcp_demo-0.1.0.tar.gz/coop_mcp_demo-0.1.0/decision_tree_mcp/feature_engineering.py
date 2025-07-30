from sklearn.preprocessing import LabelEncoder, StandardScaler

def preprocess_features(df):
    label_cols = ['job', 'marital', 'education', 'default', 'housing', 'loan', 'contact', 'month', 'poutcome']
    le = LabelEncoder()

    for col in label_cols:
        df[col] = le.fit_transform(df[col])

# 生成交互特征
    df['loan_income_ratio'] = df['balance'] / df['age']
    df['loan_to_income'] = df['balance'] / (df['age'] + 1)

    X = df.drop('y', axis=1)
    y = df['y']

# 数据标准化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled, y
