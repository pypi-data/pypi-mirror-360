from data_loader import load_data
from feature_engineering import preprocess_features
from resampling import balance_data
from train_model import train_decision_tree
from evaluate import evaluate_model
from model_io import save_model, load_model
from sklearn.model_selection import train_test_split

if __name__ == '__main__':
    file_path = 'C:/Users/admin/Documents/bank credit/data/bank.csv' # 请根据实际路径修改文件位置
    df = load_data(file_path)
    X, y = preprocess_features(df)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 数据平衡
    X_train_resampled, y_train_resampled = balance_data(X_train, y_train)

# 模型训练
    model = train_decision_tree(X_train_resampled, y_train_resampled)

# 模型评估
    evaluate_model(model, X_test, y_test)

# 保存模型
    save_model(model)

# 加载模型并做预测
    loaded_model = load_model()
    print(f"Loaded model prediction: {loaded_model.predict(X_test)}")