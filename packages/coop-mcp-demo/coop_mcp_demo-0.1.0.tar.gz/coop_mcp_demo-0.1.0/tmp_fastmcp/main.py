import numpy as np
import pandas as pd
import os
import sys
import requests
import json
from dotenv import load_dotenv
from typing import Tuple, Dict, List
from fastmcp import FastMCP
from datetime import datetime
import importlib
import traceback

# 添加项目根目录到Python路径
sys.path.append("c:/Users/admin/Desktop/coop")

# Load environment variables
load_dotenv()

mcp = FastMCP("Credit Risk MCP Server")

# Get project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Model configurations
MODEL_CONFIGS = {
    config['name'].lower(): config
    for config in [
        {            'name': 'SVM',            'module': 'SVM_mcp',            'model_path': os.path.join(PROJECT_ROOT, 'SVM_mcp', 'svm_model.pkl'),        },        {            'name': 'Decision Tree',            'module': 'decision_tree_mcp',            'model_path': os.path.join(PROJECT_ROOT, 'decision_tree_mcp', 'decision_tree_model.pkl'),        },        {            'name': 'Logistic Regression',            'module': 'logistic_regression_mcp',            'model_path': os.path.join(PROJECT_ROOT, 'logistic_regression_mcp', 'logistic_model.pkl'),        },        {            'name': 'Random Forest',            'module': 'random_forest_mcp',            'model_path': os.path.join(PROJECT_ROOT, 'random_forest_mcp', 'random_forest_model.pkl'),        }
    ]
}

@mcp.tool()
def evaluate_random_forest_credit_risk(file_path: str) -> str:
    """评估随机森林信用风险模型
    Args:
        file_path: 支持CSV(.csv)和Excel(.xlsx)格式的文件路径
    """
    if not (file_path.endswith('.csv') or file_path.endswith('.xlsx')):
        raise ValueError(f"不支持的文件格式: {file_path}。支持的格式: .csv, .xlsx")
    """使用随机森林模型评估信用风险"""
    from random_forest_mcp.random_forest_model import evaluate_random_forest_credit_risk
    return str(evaluate_random_forest_credit_risk(file_path))

@mcp.tool()
def evaluate_svm_credit_risk(file_path: str) -> str:
    """评估SVM信用风险模型
    Args:
        file_path: 支持CSV(.csv)和Excel(.xlsx)格式的文件路径
    """
    if not (file_path.endswith('.csv') or file_path.endswith('.xlsx')):
        raise ValueError(f"不支持的文件格式: {file_path}。支持的格式: .csv, .xlsx")
    """使用SVM模型评估信用风险"""
    from SVM_mcp.svm_model import evaluate_svm_credit_risk
    return str(evaluate_svm_credit_risk(file_path))

@mcp.tool()
def evaluate_decision_tree_credit_risk(file_path: str) -> str:
    """评估决策树信用风险模型
    Args:
        file_path: 支持CSV(.csv)和Excel(.xlsx)格式的文件路径
    """
    if not (file_path.endswith('.csv') or file_path.endswith('.xlsx')):
        raise ValueError(f"不支持的文件格式: {file_path}。支持的格式: .csv, .xlsx")
    """使用决策树模型评估信用风险"""
    from decision_tree_mcp.decision_tree_model import evaluate_decision_tree_credit_risk
    return str(evaluate_decision_tree_credit_risk(file_path))

@mcp.tool()
def evaluate_logistic_regression_credit_risk(file_path: str) -> str:
    """评估逻辑回归信用风险模型
    Args:
        file_path: 支持CSV(.csv)和Excel(.xlsx)格式的文件路径
    """
    if not (file_path.endswith('.csv') or file_path.endswith('.xlsx')):
        raise ValueError(f"不支持的文件格式: {file_path}。支持的格式: .csv, .xlsx")
    """使用逻辑回归模型评估信用风险"""
    from logistic_regression_mcp.logistic_regression_model import evaluate_logistic_regression_credit_risk
    return str(evaluate_logistic_regression_credit_risk(file_path))

@mcp.tool()
def evaluate_credit_risk_models(file_path: str, models: str = 'all') -> str:

    """
    Evaluate specified credit risk model (or all models) using user-provided data 
    and return the best result with AI analysis.
    """
    models = models.lower()
    results = []

    # Validate file exists
    if not os.path.exists(file_path):
        return f"错误：文件不存在 - {file_path}"

    # Validate file format
    if not (file_path.endswith('.csv') or file_path.endswith('.xlsx')):
        return f"错误：不支持的文件格式: {file_path}。支持的格式: .csv, .xlsx"

    # 模型选择
    if models == 'all':
        models_to_evaluate = list(MODEL_CONFIGS.values())
    else:
        model_config = MODEL_CONFIGS.get(models)
        if not model_config:
            return f"错误：未找到模型 '{model_name}'，可用模型：{list(MODEL_CONFIGS.keys())}"
        models_to_evaluate = [model_config]

    # 检查是否有模型可评估
    if not models_to_evaluate:
        return "没有找到可评估的模型"

    # 从第一个模型模块导入数据加载函数
    try:
        data_module = importlib.import_module(f"{models_to_evaluate[0]['module']}.data_loader")
        load_data = data_module.load_data
        df = load_data(file_path)
    except Exception as e:
        return f"""数据加载失败: {str(e)}
{traceback.format_exc()}"""

    # 遍历模型评估
    for config in models_to_evaluate:
        try:
            module_name = config["module"]
            feature_module = importlib.import_module(f"{module_name}.feature_engineering")
            modelio_module = importlib.import_module(f"{module_name}.model_io")
            eval_module = importlib.import_module(f"{module_name}.evaluate")

            preprocess = feature_module.preprocess_features
            load_model = modelio_module.load_model
            evaluate_model = eval_module.evaluate_model

            # 验证模型文件存在
            if not os.path.exists(config['model_path']):
                results.append({
                        'model': config['name'],
                        'error': f"模型文件不存在: {config['model_path']}"
                    })
                continue

            X, y = preprocess(df.copy())
            model = load_model(config['model_path'])
            accuracy, _, _, auc = evaluate_model(model, X, y)

            results.append({
                'model': config['name'],
                'accuracy': float(accuracy),
                'auc': float(auc)
            })
        except Exception as e:
            results.append({
                'model': config['name'],
                'error': f"""{str(e)}
{traceback.format_exc()}"""
            })

    valid_results = [r for r in results if 'error' not in r]
    if not valid_results:
        return "所有模型评估失败，请检查模型文件和数据格式。"

    best_model = max(valid_results, key=lambda x: x['auc'])

    # AI分析 prompt
    prompt = (
        f"分析以下信用风险预测模型的评估结果，并推荐最佳模型：\n{results}\n\n"
        f"最佳模型：{best_model['model']} (AUC: {best_model['auc']:.4f}, Accuracy: {best_model['accuracy']:.4f})\n\n"
        f"请用专业的信用风险评估视角解释各模型表现差异，并给出最终建议。"
    )

    # 调用 ModelScope API
    api_key = os.getenv("MODEL_SCOPE_API_KEY")
    base_url = os.getenv("MODEL_SCOPE_BASE_URL")

    if not api_key or not base_url:
        return "错误：ModelScope API 配置不完整，请检查 MODEL_SCOPE_API_KEY 和 MODEL_SCOPE_BASE_URL 环境变量"

    # 确保base_url以斜杠结尾
    if not base_url.endswith('/'):
        base_url += '/'

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        'model': 'Qwen/Qwen3-235B-A22B',
        'messages': [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(
            f"{base_url}chat/completions",
            headers=headers,
            data=json.dumps(data)
        )
        response.raise_for_status()
        result = response.json()
        ai_report = result['choices'][0]['message']['content']
        return f"模型评估结果：\n{results}\n\nAI 分析报告：\n{ai_report}"
    except Exception as e:
        return f"模型评估结果：\n{results}\n\nAI 分析失败：{str(e)}"

@mcp.tool()
def upload_document(file_content: str, file_name: str) -> str:
    """上传文档到服务器
    Args:
        file_content: 文档内容（base64编码）
        file_name: 文件名
    """
    # 实现文件存储逻辑
    import base64
    import os
    from pathlib import Path

    # 获取绝对路径
    upload_dir = Path(__file__).parent.parent / "uploads"
    upload_dir.mkdir(exist_ok=True)
    file_path = upload_dir / file_name

    # 验证文件类型
    supported_extensions = {'.csv', '.xlsx'}
    ext = os.path.splitext(file_name)[1].lower()
    if ext not in supported_extensions:
        return f"不支持的文件类型：{ext}，仅支持{supported_extensions}"

    try:
        # 解码并保存文件
        with open(file_path, 'wb') as f:
            f.write(base64.b64decode(file_content))
        # 返回绝对路径
        return f"文件上传成功，绝对路径：{str(file_path.resolve())}"
    except Exception as e:
        return f"文件上传失败：{str(e)}（路径：{str(file_path)}）"

if __name__ == "__main__":
    mcp.run(transport="stdio")
