import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import joblib
import logging
from typing import Tuple, Dict, Any, Union

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RandomForestCreditRiskModel:
    """随机森林信用风险评估模型"""
    def __init__(self, model_path: str = None):
        self.model = RandomForestClassifier() if not model_path else self.load_model(model_path)
        self.model_path = model_path
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.feature_names = None

    def load_data(self, file_path: str) -> pd.DataFrame:
        """加载CSV数据文件"""
        try:
            logger.info(f"加载数据文件: {file_path}")
            data = pd.read_csv(file_path)
            logger.info(f"成功加载数据，共 {data.shape[0]} 行 {data.shape[1]} 列")
            return data
        except Exception as e:
            logger.error(f"数据加载失败: {str(e)}")
            raise

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
        logger.info(f"数据划分完成，训练集: {self.X_train.shape[0]} 样本, 测试集: {self.X_test.shape[0]} 样本")

    def train(self, **kwargs) -> None:
        """训练模型"""
        if self.X_train is None or self.y_train is None:
            raise ValueError("请先加载并划分数据")
        logger.info("开始训练随机森林模型...")
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
            joblib.dump(self.model, file_path)
            self.model_path = file_path
            logger.info(f"模型成功保存到: {file_path}")
        except Exception as e:
            logger.error(f"模型保存失败: {str(e)}")
            raise

    def load_model(self, file_path: str) -> RandomForestClassifier:
        """从文件加载模型"""
        try:
            logger.info(f"从文件加载模型: {file_path}")
            return joblib.load(file_path)
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
            raise

    def predict(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """使用模型进行预测"""
        if not isinstance(data, pd.DataFrame):
            data = pd.DataFrame(data, columns=self.feature_names)
        y_pred = self.model.predict(data)
        y_prob = self.model.predict_proba(data)[:, 1] if hasattr(self.model, 'predict_proba') else None
        return y_pred, y_prob

    def get_feature_importance(self) -> Dict[str, float]:
        """获取特征重要性"""
        if not hasattr(self.model, 'feature_importances_'):
            raise AttributeError("模型不支持特征重要性分析")
        return dict(zip(self.feature_names, self.model.feature_importances_))

def evaluate_random_forest_credit_risk(data: Union[str, pd.DataFrame] = None, file_path: str = None, model_path: str = None, target_column: str = None,** train_kwargs) -> Dict[str, Any]:
    """
    评估随机森林信用风险模型的主函数，供LLM调用
    
    参数:
        file_path: CSV数据文件路径
        model_path: 预训练模型路径（可选）
        **train_kwargs: 训练参数
    
    返回:
        包含评估结果的字典
    """
    model = RandomForestCreditRiskModel(model_path)
    if data is None and file_path is None:
        raise ValueError("必须提供data或file_path参数")
    if data is None:
        data = model.load_data(file_path)
    elif isinstance(data, str):
        data = model.load_data(data)
    X, y = model.preprocess_data(data, target_column)
    model.split_data(X, y)
    
    if not model_path:
        model.train(**train_kwargs)
        # 可以选择保存新训练的模型
        # model.save_model(f"random_forest_model_{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}.pkl")
    
    evaluation_results = model.evaluate()
    feature_importance = model.get_feature_importance()
    
    return {
        "model_name": "Random Forest",
        "evaluation_metrics": evaluation_results,
        "feature_importance": feature_importance,
        "model_path": model.model_path
    }

if __name__ == "__main__":
    # 示例用法
    result = evaluate_random_forest_credit_risk("data.csv")
    print(result)