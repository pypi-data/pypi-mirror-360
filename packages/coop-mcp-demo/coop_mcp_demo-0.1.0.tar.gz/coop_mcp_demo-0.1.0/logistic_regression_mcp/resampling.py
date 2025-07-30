# resampling.py
def balance_data(X, y):
    from imblearn.over_sampling import RandomOverSampler
    ros = RandomOverSampler(random_state=42)
    return ros.fit_resample(X, y)