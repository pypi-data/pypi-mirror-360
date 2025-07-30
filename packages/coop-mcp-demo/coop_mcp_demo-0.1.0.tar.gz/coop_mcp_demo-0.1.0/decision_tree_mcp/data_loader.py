import pandas as pd
import chardet

def load_data(file_path: str) -> 'pd.DataFrame':
    """从CSV或Excel文件加载数据并预处理目标变量。"""
    if file_path.endswith('.csv'):
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read(10000))  # 检测前1万字节
        encoding = result['encoding']
        df = pd.read_csv(file_path, delimiter=';', encoding=encoding)
    elif file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"不支持的文件格式: {file_path}。支持的格式: .csv, .xlsx")
    
    # 将目标变量转换为数值
    df['y'] = df['y'].map({'yes': 1, 'no': 0})
    return df