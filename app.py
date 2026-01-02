import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

# 設定繪圖風格
sns.set(style="whitegrid")
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] # 解決中文亂碼問題
plt.rcParams['axes.unicode_minus'] = False

def load_and_explore_data(filepath):
    """
    載入並初步探索資料
    """
    try:
        df = pd.read_csv(filepath)
        print("資料載入成功！")
        print(f"資料維度: {df.shape}")
        
        print("\n前 5 筆資料:")
        print(df.head())
        
        print("\n資料資訊:")
        print(df.info())
        
        print("\n數值型欄位統計:")
        print(df.describe())
        
        print("\n缺失值統計:")
        missing_values = df.isnull().sum()
        print(missing_values[missing_values > 0])
        
        return df
    except FileNotFoundError:
        print(f"錯誤: 找不到檔案 {filepath}")
        return None

def preprocess_data(df, target_column):
    """
    資料前處理：包含缺失值填補、特徵編碼與標準化
    """
    # 分離特徵與目標變數
    X = df.drop(target_column, axis=1)
    y = df[target_column]

    # 定義數值型與類別型特徵
    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns
    categorical_features = X.select_dtypes(include=['object', 'category']).columns

    print(f"\n數值型特徵: {list(numeric_features)}")
    print(f"類別型特徵: {list(categorical_features)}")

    # 建立數值型特徵處理管道 (填補缺失值 + 標準化)
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    # 建立類別型特徵處理管道 (填補缺失值 + OneHotEncoding)
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])

    # 整合處理器
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])

    return X, y, preprocessor

def train_model(X, y, preprocessor):
    """
    模型訓練與超參數調整
    """
    # 分割訓練集與測試集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 建立完整的訓練管道
    clf = Pipeline(steps=[('preprocessor', preprocessor),
                          ('classifier', RandomForestClassifier(random_state=42))])

    # 設定超參數網格
    param_grid = {
        'classifier__n_estimators': [100, 200],
        'classifier__max_depth': [None, 10, 20],
        'classifier__min_samples_split': [2, 5],
        'classifier__min_samples_leaf': [1, 2]
    }

    # 使用 Grid Search 進行交叉驗證與參數優化
    print("\n開始進行模型訓練與參數優化 (Grid Search)...")
    grid_search = GridSearchCV(clf, param_grid, cv=5, n_jobs=-1, verbose=1, scoring='accuracy')
    grid_search.fit(X_train, y_train)

    print(f"最佳參數: {grid_search.best_params_}")
    print(f"最佳交叉驗證分數: {grid_search.best_score_:.4f}")

    return grid_search.best_estimator_, X_test, y_test

def evaluate_model(model, X_test, y_test):
    """
    模型評估
    """
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else None

    print("\n分類報告:")
    print(classification_report(y_test, y_pred))

    print("\n混淆矩陣:")
    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Confusion Matrix')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.show()

    if y_proba is not None:
        auc = roc_auc_score(y_test, y_proba)
        print(f"\nROC AUC Score: {auc:.4f}")

# --- 主程式執行區 ---
if __name__ == "__main__":
    # 假設資料集名稱為 'data.csv'，請替換為實際路徑
    data_path = 'data.csv' 
    
    # 載入資料
    df = load_and_explore_data(data_path)

    if df is not None:
        # 假設目標欄位名稱為 'target'，請替換為實際欄位名稱
        target_col = 'target' 
        
        # 檢查目標欄位是否存在
        if target_col in df.columns:
            # 資料前處理
            X, y, preprocessor = preprocess_data(df, target_col)
            
            # 模型訓練
            best_model, X_test, y_test = train_model(X, y, preprocessor)
            
            # 模型評估
            evaluate_model(best_model, X_test, y_test)
        else:
            print(f"錯誤: 資料集中找不到目標欄位 '{target_col}'")
