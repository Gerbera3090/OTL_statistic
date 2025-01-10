import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()
# 두 데이터베이스의 연결 정보
db_config_primary = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'port': os.getenv('DB_PORT'),
}

db_config_secondary = {
    'user': os.getenv('DB_USER_SECONDARY'),
    'password': os.getenv('DB_PASSWORD_SECONDARY'),
    'host': os.getenv('DB_HOST_SECONDARY'),
    'database': os.getenv('DB_NAME_SECONDARY'),
    'port': os.getenv('DB_PORT_SECONDARY'),
}

def connect_to_database(config):
    """
    주어진 DB 설정으로 MySQL에 연결.
    """
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            print(f"Connected to {config['host']}:{config['port']}/{config['database']}")
        return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

def fetch_query_results(cursor, query):
    """
    주어진 쿼리를 실행하고 결과를 반환.
    """
    cursor.execute(query)
    return cursor.fetchall()

def compare_results(primary_results, secondary_results):
    """
    두 데이터베이스 결과를 비교하여 동일한 student_id를 반환.
    """
    # 결과를 딕셔너리로 변환
    primary_dict = {row[0]: (row[1], row[2]) for row in primary_results}
    secondary_dict = {row[0]: (row[1], row[2]) for row in secondary_results}

    # 공통 student_id에서 count(*)와 sum(credit)이 같은 경우 필터링
    matching_ids = [
        student_id
        for student_id in primary_dict
        if student_id in secondary_dict and primary_dict[student_id] == secondary_dict[student_id]
    ]

    return matching_ids

def calculate_difference_and_sort_dropped_lecture(primary_results, secondary_results):
    """
    primary_results와 secondary_results를 비교하여 count(id)의 차이를 계산하고 내림차순 정렬.
    """
    # 결과를 딕셔너리로 변환 (lecture_id를 키로 사용)
    primary_dict = {row[1]: [row[0], row[2], row[3]] for row in primary_results}  # {lecture_id: count(id)}
    secondary_dict = {row[1]: [row[0], row[2], row[3]] for row in secondary_results}  # {lecture_id: count(id)}

    # 공통 lecture_id에 대해 count(id) 차이 계산
    differences = []
    for lecture_id in primary_dict:
        if lecture_id in secondary_dict:
            difference = primary_dict[lecture_id][0] - secondary_dict[lecture_id][0]
            differences.append((lecture_id, difference, primary_dict[lecture_id][1], primary_dict[lecture_id][2])) 

    # 차이를 기준으로 내림차순 정렬
    sorted_differences = sorted(differences, key=lambda x: x[1], reverse=True)

    return sorted_differences

def calculate_difference_and_sort_hottest_lecture(primary_results, secondary_results):
    """
    primary_results와 secondary_results를 비교하여 count(id)의 차이를 계산하고 내림차순 정렬.
    """
    # 결과를 딕셔너리로 변환 (lecture_id를 키로 사용)
 
    # 차이를 기준으로 내림차순 정렬
    sorted_differences = sorted(primary_results, key=lambda x: x[0] / x[3] if x[3] != 0 else 0, reverse=True)

    return sorted_differences

def calculate_difference_and_sort_many_lecture(primary_results, secondary_results):
    """
    primary_results와 secondary_results를 비교하여 count(id)의 차이를 계산하고 내림차순 정렬.
    """
    # 결과를 딕셔너리로 변환 (lecture_id를 키로 사용)
    primary_dict = {row[1]: [row[0], row[2]] for row in primary_results}  # {lecture_id: count(id)}
    secondary_dict = {row[1]: [row[0], row[2]] for row in secondary_results}  # {lecture_id: count(id)}

    # 공통 lecture_id에 대해 count(id) 차이 계산
    differences = []
    for lecture_id in primary_dict:
        if lecture_id in secondary_dict:
            difference = primary_dict[lecture_id][0] - secondary_dict[lecture_id][0]
            differences.append((lecture_id, difference, primary_dict[lecture_id][1] ))

    # 차이를 기준으로 내림차순 정렬
    sorted_differences = sorted(differences, key=lambda x: x[1], reverse=True)

    return sorted_differences

def check_data_in_databases():
    """
    두 데이터베이스에 동시에 접속하여 데이터를 확인.
    """
    try:
        # 두 DB 연결
        conn_primary = connect_to_database(db_config_primary)
        conn_secondary = connect_to_database(db_config_secondary)

        if conn_primary and conn_secondary:
            # 커서 생성
            cursor_primary = conn_primary.cursor()
            cursor_secondary = conn_secondary.cursor()



            ### 1. 
            # 쿼리 실행
            query = """
            SELECT student_id, COUNT(*), SUM(credit)
            FROM susins
            WHERE (student_id DIV 1000) % 10 = 0
            OR (student_id DIV 1000) % 10 = 1
            GROUP BY student_id
            ORDER BY SUM(credit) DESC;
            """
            primary_results = fetch_query_results(cursor_primary, query)
            secondary_results = fetch_query_results(cursor_secondary, query)

            # 비교하여 동일한 student_id 추출
            matching_ids = compare_results(primary_results, secondary_results)

            # 결과 출력
            print("\nMatching student_ids with identical count(*) and SUM(credit):")
            # for student_id in matching_ids:
            #     print(student_id)
            print(len(matching_ids), "matching student_ids found.")

            ## 2.
            query2 = """
            SELECT student_id, id
            FROM susins
            WHERE (student_id DIV 1000) % 10 = 0
            OR (student_id DIV 1000) % 10 = 1
            """
            primary_results2 = fetch_query_results(cursor_primary, query2)
            secondary_results2 = fetch_query_results(cursor_secondary, query2)
            print(len(primary_results2))
            print(len(secondary_results2))
            print(len(primary_results2) - len(secondary_results2))
            
            ## 3. 삭제된 학점
            query3 = """
            SELECT  sum(credit)
            FROM susins
            WHERE (student_id DIV 1000) % 10 = 0
            OR (student_id DIV 1000) % 10 = 1
            """
            primary_results3 = fetch_query_results(cursor_primary, query3)
            secondary_results3 = fetch_query_results(cursor_secondary, query3)
            print(primary_results3[0])
            print(secondary_results3[0])
            print(primary_results3[0][0] - secondary_results3[0][0])
            
            ## 4. 가장 많이 떨어진 과목 Top 5
            query4 = """
            SELECT count(id), lecture_id, max(title), max(class_no)
            FROM susins
            WHERE `limit` > 0
            GROUP BY lecture_id
            """
            primary_results4 = fetch_query_results(cursor_primary, query4)
            secondary_results4 = fetch_query_results(cursor_secondary, query4)
            print(len(primary_results4))
            print(len(secondary_results4))

            sorted_differences = calculate_difference_and_sort_dropped_lecture(primary_results4, secondary_results4)
            # 결과 출력
            print("\nLecture ID Differences (sorted by difference):")
            print(f"{'Lecture ID':<15}{'Difference':<10}")
            print("-" * 25)
            for lecture_id, difference, title, classNo in sorted_differences[:10]:
                print(f"{lecture_id:<15}{difference:<10}{title} {classNo}")
            
             ## 5. 가장 많이 몰린 과목 Top 5
            query5 = """
            SELECT count(id), lecture_id, max(title), max(class_no)
            FROM susins
            WHERE ((student_id DIV 1000) % 10 = 0 OR (student_id DIV 1000) % 10 = 1) 
                
            GROUP BY lecture_id
            ORDER BY count(id) DESC
            """
            primary_results5 = fetch_query_results(cursor_primary, query5)
            secondary_results5 = fetch_query_results(cursor_secondary, query5)
            print(len(primary_results5))
            print(len(secondary_results5))

            
            # 결과 출력
            print("\nLecture ID Many (sorted by count):")
            print(f"{'Lecture ID':<15}{'count':<10}")
            print("-" * 25)
            for lecture_id, difference, title, classNo in primary_results5[:10]:
                print(f"{lecture_id:<15}{difference:<10}{title}{classNo}")
            
            ## 6. 가장 핫한 과목 Top 5
            query6 = """
            SELECT count(id), lecture_id, max(title), max(`limit`), max(class_no)
            FROM susins
            WHERE (student_id DIV 1000) % 10 = 0 OR (student_id DIV 1000) % 10 = 1 
                AND `limit` > 0
            GROUP BY lecture_id
            ORDER BY count(id) DESC
            """
            primary_results6 = fetch_query_results(cursor_primary, query6)
            secondary_results6 = fetch_query_results(cursor_secondary, query6)
            print((primary_results6[0]))
            print(len(secondary_results6))

            sorted_differences2 = calculate_difference_and_sort_hottest_lecture(primary_results6, secondary_results6)
            
            # 결과 출력
            print("\nLecture ID Many (sorted by count):")
            print(f"{'Lecture ID':<15}{'count':<10}")
            print("-" * 25)
            for cnt, lecture_id, title, limit, classNo in sorted_differences2[:10]:
                print(f"{lecture_id:<15}{cnt / limit:<10} : {limit} | {title} {classNo}")

            ## 7. 정원이 찬 과목 수 / 전체 과목 수
            query7 = """
            SELECT count(id), lecture_id, max(title), max(`limit`)
            FROM susins
            WHERE `limit` > 0 
            AND title not in ( '논문연구(박사)', '논문연구(석사)', '논문연구 (박사)', '개별연구', '논문연구 (논문석사)', '졸업연구','논문연구 (석사)' )
            GROUP BY lecture_id
            HAVING count(id) >= max(`limit`)
            """ 
            primary_results7 = fetch_query_results(cursor_primary, query7)
            secondary_results7 = fetch_query_results(cursor_secondary, query7)
            print(len(primary_results7))
            print(len(secondary_results7))

            query8 = """
            SELECT count(id), lecture_id, max(title), max(`limit`)
            FROM susins
            WHERE title not in( '논문연구(박사)', '논문연구(석사)', '논문연구 (박사)', '개별연구', '논문연구 (논문석사)', '졸업연구','논문연구 (석사)' )
            GROUP BY lecture_id
            """
            primary_results8 = fetch_query_results(cursor_primary, query8)
            secondary_results8 = fetch_query_results(cursor_secondary, query8)
            print(len(primary_results8))
            print(len(secondary_results8))

            ## 분반이 가장 많은 과목
            query9 = """
            SELECT count(DISTINCT(lecture_id)), course_id, max(title), max(`limit`)
            FROM susins
            WHERE title not in( '논문연구(박사)', '논문연구(석사)', '논문연구 (박사)', '개별연구', '논문연구 (논문석사)', '졸업연구','논문연구 (석사)' )
            GROUP BY course_id
            ORDER BY count(DISTINCT(lecture_id)) DESC
            """
            result9 = fetch_query_results(cursor_primary, query9)
            for row in result9[:20]:
                print(row)
            print(sum([row[0] for row in result9]))

            ## 10. 학생이 가장 많이 듣는 과목
            query10 = """
            SELECT count(distinct(lecture_id))
            FROM susins
            
            """
            result10 = fetch_query_results(cursor_primary, query10)
            for row in result10[:20]:
                print(row)
            # 커서 및 연결 닫기
            cursor_primary.close()
            cursor_secondary.close()
        else:
            print("Failed to connect to one or both databases.")


    finally:
        if conn_primary and conn_primary.is_connected():
            conn_primary.close()
            print("\nPrimary database connection closed.")
        if conn_secondary and conn_secondary.is_connected():
            conn_secondary.close()
            print("Secondary database connection closed.")

# 실행
if __name__ == "__main__":
    check_data_in_databases()