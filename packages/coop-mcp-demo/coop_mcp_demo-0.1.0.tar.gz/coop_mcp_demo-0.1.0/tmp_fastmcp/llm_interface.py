import re
import sys
import os
from pathlib import Path
from typing import Dict, Optional

# 添加项目根目录到系统路径
sys.path.append(str(Path(__file__).parent.parent))
from random_forest_mcp.random_forest_model import evaluate_random_forest_credit_risk as evaluate_random_forest
from SVM_mcp.svm_model import evaluate_svm_credit_risk as evaluate_svm
from decision_tree_mcp.decision_tree_model import evaluate_decision_tree_credit_risk as evaluate_decision_tree
from logistic_regression_mcp.logistic_regression_model import evaluate_logistic_regression_credit_risk as evaluate_logistic_regression

class LLMDataPredictionInterface:
    def __init__(self):
        # 支持的模型列表及自动选择规则
        self.system_prompt = "你是一个数据预测专家，可以使用提供的工具来完成各种数据预测任务。你可以调用以下工具来完成任务：\n1. upload_document: 上传文档到服务器，需要file_content（base64编码）和file_name参数，调用示例：<|FunctionCallBegin|>[{\"name\":\"upload_document\",\"parameters\":{\"file_content\":\"base64编码内容\",\"file_name\":\"data.csv\"}}]<|FunctionCallEnd|>。文件上传成功后，使用返回的绝对路径调用评估工具。\n2. evaluate_random_forest: 使用随机森林模型进行预测，参数: data(可选数据对象), file_path(可选文件路径), target_column(可选目标列名)\n3. evaluate_svm: 使用SVM模型进行预测，参数: data(可选数据对象), file_path(可选文件路径), target_column(可选目标列名)\n4. evaluate_decision_tree: 使用决策树模型进行预测，参数: data(可选数据对象), file_path(可选文件路径), target_column(可选目标列名)\n5. evaluate_logistic_regression: 使用逻辑回归模型进行预测，参数: data(可选数据对象), file_path(可选文件路径), target_column(可选目标列名)"
        self.supported_models = {
            'random_forest': 'Random Forest',
            'svm': 'SVM',
            'decision_tree': 'Decision Tree',
            'logistic_regression': 'Logistic Regression'
        }
        # 更新文件路径模式匹配
        # 更新文件路径模式匹配
        self.file_path_pattern = r'(?:[A-Za-z]:[\\/]|uploads[\\/])[^"']*?\.(?:csv|xlsx)'

    def parse_user_query(self, user_query: str) -> Dict[str, Optional[str]]:
        """解析用户查询，提取文件路径和模型选择"
        result = {
            'file_path': None,
            'model_name': None,
            'data': None,
            'target_column': None
        }

        # 提取CSV文件路径
        path_match = re.search(self.file_path_pattern, user_query)
        if path_match:
            result['file_path'] = path_match.group(0)

        # 提取模型名称（如果用户指定）
        for model_key, model_name in self.supported_models.items():
            if model_key in user_query.lower() or model_name.lower() in user_query.lower():
                result['model_name'] = model_name
                break

        # 提取目标列名
        target_match = re.search(r'target_column[:=]?[\s]*([^,\s]+)', user_query.lower())
        if target_match:
            result['target_column'] = target_match.group(1)

        # 检查是否有内嵌数据（简化处理，实际场景可能需要更复杂的解析）
        if 'data=' in user_query.lower():
            data_match = re.search(r'data=([^,]+)', user_query)
            if data_match:
                result['data'] = data_match.group(1)

        return result

    def auto_select_model(self, file_path: str) -> str:
        "基于数据特征自动选择最合适的模型"
        # 这里可以实现更复杂的模型选择逻辑
        # 简化版：根据文件名或数据特征选择模型
        file_name = os.path.basename(file_path).lower()

        if 'complex' in file_name or 'multi' in file_name:
            return self.supported_models['random_forest']  # 复杂数据优先使用随机森林
        elif 'simple' in file_name or 'linear' in file_name:
            return self.supported_models['logistic_regression']  # 简单线性数据使用逻辑回归
        elif 'nonlinear' in file_name:
            return self.supported_models['svm']  # 非线性数据使用SVM
        else:
            return self.supported_models['decision_tree']  # 默认使用决策树

    def process_query(self, user_query: str) -> str:
        """处理用户查询并返回评估结果"""
        # 解析用户查询
        parsed_data = self.parse_user_query(user_query)

        if not parsed_data['file_path']:
            return "无法识别CSV文件路径，请提供有效的文件路径。"

        # 验证文件是否存在
        if not os.path.exists(parsed_data['file_path']):
            return f"文件不存在: {parsed_data['file_path']}"

        # 确定模型（用户指定或自动选择）
        model_name = parsed_data['model_name'] or self.auto_select_model(parsed_data['file_path'])

        # 调用评估函数
        try:
            # 根据模型名称选择对应的评估函数
            model_functions = {
                'Random Forest': evaluate_random_forest,
                'SVM': evaluate_svm,
                'Decision Tree': evaluate_decision_tree,
                'Logistic Regression': evaluate_logistic_regression
            }
            evaluation_function = model_functions.get(model_name)
            if not evaluation_function:
                return f"不支持的模型: {model_name}"
            
            # 准备评估参数
            eval_params = {}
            if 'data' in parsed_data and parsed_data['data'] is not None:
                eval_params['data'] = parsed_data['data']
            else:
                eval_params['file_path'] = parsed_data['file_path']
            if 'target_column' in parsed_data and parsed_data['target_column']:
                eval_params['target_column'] = parsed_data['target_column']
            
            evaluation_result = evaluation_function(**eval_params)

            # 格式化结果返回给LLM
            return f"已使用{model_name}模型完成数据预测。\n预测结果：{evaluation_result}"
        except Exception as e:
            return f"评估过程中出错: {str(e)}"

# LLM调用入口
def llm_process_query(user_query: str) -> str:
    interface = LLMDataPredictionInterface()
    return interface.process_query(user_query)

# 测试代码
if __name__ == '__main__':
    test_query = "请分析C:\data\data.csv文件的数据"
    print(llm_process_query(test_query))