# train_model.py
def train_logistic(X, y):
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import GridSearchCV
    param_grid = {'C': [0.1, 1, 10], 'solver': ['liblinear', 'saga'], 'penalty': ['l1', 'l2']}
    grid = GridSearchCV(LogisticRegression(max_iter=1000), param_grid, cv=5, n_jobs=-1)
    grid.fit(X, y)
    return grid.best_estimator_