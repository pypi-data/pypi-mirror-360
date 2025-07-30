import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
import joblib
import logging
from typing import Tuple, Dict, Any, Optional
from .data_loader import load_data

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LogisticRegressionCreditRiskModel:
    """逻辑回归信用风险评估模型"""
    def __init__(self, model_path: str = None):
        self.model = LogisticRegression(max_iter=1000) if not model_path else self.load_model(model_path)
        self.model_path = model_path
        self.scaler = StandardScaler()
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.feature_names = None

    def preprocess_data(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """数据预处理，包括特征工程和目标变量分离"""
        # 假设最后一列是目标变量
        self.feature_names = data.columns[:-1].tolist()
        X = data.iloc[:, :-1]
        y = data.iloc[:, -1]
        logger.info(f"数据预处理完成，特征数: {X.shape[1]}, 样本数: {X.shape[0]}")
        return X, y

    def split_data(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2, random_state: int = 42) -> None:
        """划分训练集和测试集"""
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        # 逻辑回归需要特征标准化
        self.X_train = self.scaler.fit_transform(self.X_train)
        self.X_test = self.scaler.transform(self.X_test)
        logger.info(f"数据划分及标准化完成，训练集: {self.X_train.shape[0]} 样本, 测试集: {self.X_test.shape[0]} 样本")

    def train(self, **kwargs) -> None:
        """训练模型"""
        if self.X_train is None or self.y_train is None:
            raise ValueError("请先加载并划分数据")
        logger.info("开始训练逻辑回归模型...")
        self.model.set_params(**kwargs)
        self.model.fit(self.X_train, self.y_train)
        logger.info("模型训练完成")

    def evaluate(self) -> Dict[str, float]:
        """评估模型性能"""
        if self.X_test is None or self.y_test is None:
            raise ValueError("请先加载并划分数据")
        y_pred = self.model.predict(self.X_test)
        y_prob = self.model.predict_proba(self.X_test)[:, 1] if hasattr(self.model, 'predict_proba') else None

        metrics = {
            'accuracy': accuracy_score(self.y_test, y_pred),
            'precision': precision_score(self.y_test, y_pred),
            'recall': recall_score(self.y_test, y_pred),
            'f1': f1_score(self.y_test, y_pred)
        }

        if y_prob is not None:
            metrics['auc'] = roc_auc_score(self.y_test, y_prob)

        logger.info(f"模型评估结果: {metrics}")
        return metrics

    def save_model(self, file_path: str) -> None:
        """保存模型到文件"""
        try:
            # 同时保存模型和标准化器
            joblib.dump({'model': self.model, 'scaler': self.scaler}, file_path)
            self.model_path = file_path
            logger.info(f"模型和标准化器成功保存到: {file_path}")
        except Exception as e:
            logger.error(f"模型保存失败: {str(e)}")
            raise

    def load_model(self, file_path: str) -> LogisticRegression:
        """从文件加载模型"""
        try:
            logger.info(f"从文件加载模型: {file_path}")
            data = joblib.load(file_path)
            self.model = data['model']
            self.scaler = data['scaler']
            return self.model
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
            raise

    def predict(self, data: pd.DataFrame) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """使用模型进行预测"""
        if not isinstance(data, pd.DataFrame):
            data = pd.DataFrame(data, columns=self.feature_names)
        scaled_data = self.scaler.transform(data)
        y_pred = self.model.predict(scaled_data)
        y_prob = self.model.predict_proba(scaled_data)[:, 1] if hasattr(self.model, 'predict_proba') else None
        return y_pred, y_prob

    def get_coefficients(self) -> Dict[str, float]:
        """获取特征系数"""
        return dict(zip(self.feature_names, self.model.coef_[0]))

def evaluate_logistic_regression_credit_risk(file_path: str, model_path: str = None, **train_kwargs) -> Dict[str, Any]:
    """
    评估逻辑回归信用风险模型的主函数，供LLM调用
    
    参数:
        file_path: CSV数据文件路径
        model_path: 预训练模型路径（可选）
        **train_kwargs: 训练参数
    
    返回:
        包含评估结果的字典
    """
    model = LogisticRegressionCreditRiskModel(model_path)
    data = load_data(file_path)
    X, y = model.preprocess_data(data)
    model.split_data(X, y)
    
    if not model_path:
        model.train(** train_kwargs)
        # 可以选择保存新训练的模型
        # model.save_model(f"logistic_regression_model_{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}.pkl")
    
    evaluation_results = model.evaluate()
    coefficients = model.get_coefficients()
    
    return {
        "model_name": "Logistic Regression",
        "evaluation_metrics": evaluation_results,
        "coefficients": coefficients,
        "model_path": model.model_path
    }

if __name__ == "__main__":
    # 示例用法
    result = evaluate_logistic_regression_credit_risk("data.csv")
    print(result)