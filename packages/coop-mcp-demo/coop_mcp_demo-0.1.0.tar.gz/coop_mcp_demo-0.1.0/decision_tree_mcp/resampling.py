from imblearn.over_sampling import RandomOverSampler
def balance_data(X_train, y_train):
    ros = RandomOverSampler(random_state=42)
    return ros.fit_resample(X_train, y_train)