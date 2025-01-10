import os
import pandas as pd

def infer_data_type(col_data):
    """
    간단한 데이터 타입 추론 함수
    """
    if pd.api.types.is_integer_dtype(col_data):
        return "INT"
    elif pd.api.types.is_float_dtype(col_data):
        return "FLOAT"
    elif pd.api.types.is_datetime64_any_dtype(col_data):
        return "DATETIME"
    else:
        max_length = col_data.astype(str).map(len).max()  # 최대 길이 계산
        return f"VARCHAR({max_length})"


def csv_to_sqldump(file_path, table_name, output_file):
    try:
        # CSV 파일 읽기
        df = pd.read_csv(file_path)

        # DDL 생성
        desc_info = []
        for col in df.columns:
            col_data = df[col]
            dtype = infer_data_type(col_data)
            is_nullable = "NULL" if col_data.isnull().any() else "NOT NULL"
            desc_info.append((col, dtype, is_nullable))

        ddl = f"CREATE TABLE `{table_name}` (\n"
        ddl += ",\n".join([f"  `{field}` {dtype} {nullable}" for field, dtype, nullable in desc_info])
        ddl += "\n);\n\n"

        # INSERT 문 생성
        insert_statements = []
        for _, row in df.iterrows():
            values = ", ".join(
                ["'{}'".format(str(value).replace('\'', '\'\'')) if pd.notnull(value) else "NULL" for value in row]
            )
            insert_statements.append(f"INSERT INTO `{table_name}` ({', '.join([f'`{col}`' for col in df.columns])}) VALUES ({values});")

        # 결과 저장
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"-- MySQL dump for table `{table_name}`\n\n")
            f.write(ddl)  # DDL 작성
            f.write("\n".join(insert_statements))  # INSERT 문 작성

        print(f"MySQL dump file created successfully: {output_file}")

    except Exception as e:
        print(f"Error processing the CSV file {file_path}: {e}")


def main():
    # 사용자 입력: CSV 파일 경로 및 테이블 이름
    # csv_file = input("Enter the path to the CSV file: ").strip()
    # table_name = input("Enter the table name: ").strip()

    # 사용법
    csv_file = './dbs/Result_42.csv'   #CSV 파일 경로
    table_name = 'susins'   # 생성할 MySQL 테이블 이름
    dump_file = 'susin_output_dump.sql'    # 출력 MySQL dump 파일 이름


    # 파일 존재 여부 확인
    if not os.path.exists(csv_file):
        print(f"File does not exist: {csv_file}")
        return

    # 출력 파일 설정
    output_file = f"new_{table_name}_dump.sql"

    # CSV를 SQL dump로 변환
    csv_to_sqldump(csv_file, table_name, output_file)


if __name__ == "__main__":
    main()

