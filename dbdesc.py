import os
import pandas as pd

def analyze_csv(file_path):
    try:
        # CSV 파일 읽기
        df = pd.read_csv(file_path)

        # 출력할 데이터 준비
        desc_info = []
        for col in df.columns:
            col_data = df[col]
            print(col_data)
            # 데이터 유형 추정
            if pd.api.types.is_integer_dtype(col_data):
                dtype = "INT"
            elif pd.api.types.is_float_dtype(col_data):
                dtype = "FLOAT"
            elif pd.api.types.is_datetime64_any_dtype(col_data):
                dtype = "DATETIME"
            else:
                max_length = col_data.astype(str).map(len).max()  # 최대 길이
                dtype = f"VARCHAR({max_length})"

            # NULL 가능 여부 확인
            is_nullable = "YES" if col_data.isnull().any() else "NO"

            # 결과 추가
            desc_info.append((col, dtype, is_nullable))

        # DESC와 유사한 출력
        print(f"{'Field':<20}{'Type':<20}{'Null':<10}")
        print("-" * 50)
        for field, dtype, nullable in desc_info:
            print(f"{field:<20}{dtype:<20}{nullable:<10}")

    except Exception as e:
        print(f"Error reading the CSV file {file_path}: {e}")


def process_all_csv_files(folder_path):
    # 폴더 내의 모든 CSV 파일 가져오기
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    if not csv_files:
        print(f"No CSV files found in the folder: {folder_path}")
        return

    # 각 CSV 파일 분석
    for csv_file in csv_files:
        file_path = os.path.join(folder_path, csv_file)
        print("="*50)
        print(f"\nAnalyzing file: {csv_file}")
        analyze_csv(file_path)


# 실행
# CSV 파일이 저장된 폴더
folder_path = "dbs" 
process_all_csv_files(folder_path)