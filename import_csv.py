"""
CSV 데이터 임포트 모듈.

이 모듈은 크롤링된 강의 수강평 CSV 파일을 읽어 SQLite 데이터베이스에 저장합니다.
CSV 파일의 학수번호를 기준으로 강의를 생성하거나 기존 강의에 수강평을 추가합니다.

입력 파일 형식:
    - CSV 파일 (UTF-8-BOM 인코딩 지원)
    - 필수 컬럼: course_code, review
    - 선택 컬럼: professor, lecture_id, year, semester

사용법:
    python import_csv.py

주의사항:
    - init_db.py를 먼저 실행하여 데이터베이스를 초기화해야 합니다.
    - CSV 파일 경로: crawling/klue_reviews_multi.csv
"""

import csv
import sqlite3
import os

# =============================================================================
# 경로 및 상수 설정
# =============================================================================

# 현재 파일 경로 기준 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "crawling", "klue_reviews_multi.csv")
DB_NAME = os.path.join(BASE_DIR, "hackathon.db")

# 학수번호 -> 한글 강의명 매핑 테이블
# 새로운 과목 추가 시 이 딕셔너리에 매핑을 추가해야 합니다.
COURSE_NAME_MAP = {
        "COSE111": "전산수학I",
        "COSE341": "운영체제",
        "COSE389": "기업가정신과리더십",
}


# =============================================================================
# 메인 함수
# =============================================================================

def import_data() -> None:
    """
    CSV 파일에서 수강평 데이터를 읽어 데이터베이스에 저장합니다.

    이 함수는 다음 작업을 수행합니다:
        1. CSV 파일 존재 여부 확인
        2. UTF-8-BOM 인코딩으로 CSV 파일 읽기
        3. 각 행에 대해:
           - 학수번호로 기존 강의 조회 또는 새 강의 생성
           - 수강평을 course_reviews 테이블에 저장

    Raises:
        파일이 없거나 필수 컬럼이 없는 경우 에러 메시지를 출력하고 종료합니다.

    Note:
        - 빈 course_code나 review는 건너뜁니다.
        - 100개 단위로 진행 상황을 출력합니다.
    """
    if not os.path.exists(CSV_FILE):
        print(f"❌ 오류: 파일을 찾을 수 없습니다.")
        print(f"   👉 경로: {CSV_FILE}")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    print(f"📥 CSV 데이터 삽입 시작... (파일: {os.path.basename(CSV_FILE)})")

    try:
        # [핵심 수정] encoding='utf-8-sig': 엑셀/윈도우 저장 시 생기는 BOM 문자(\ufeff) 제거
        with open(CSV_FILE, newline='', encoding='utf-8-sig') as f:
            # 헤더의 앞뒤 공백 제거 (skipinitialspace=True)
            reader = csv.DictReader(f, skipinitialspace=True)

            # 헤더(컬럼명) 확인용 (디버깅)
            headers = reader.fieldnames
            print(f"ℹ️  감지된 컬럼: {headers}")

            # 필수 컬럼이 있는지 검사
            if not headers or 'course_code' not in headers:
                print("❌ 'course_code' 컬럼을 찾을 수 없습니다!")
                print("   👉 CSV 파일의 첫 번째 줄이 'course_code,professor,...' 형식인지 확인해주세요.")
                return

            count = 0
            for row in reader:
                # 딕셔너리 키 접근 시 공백 제거 처리
                course_code = row.get('course_code', '').strip()
                review_content = row.get('review', '').strip()

                if not course_code or not review_content:
                    continue

                # 강의명 매핑
                course_name = COURSE_NAME_MAP.get(course_code, course_code)

                # 1. 강의 존재 여부 확인 (학수번호 기준)
                cursor.execute("SELECT id FROM courses WHERE course_code = ?", (course_code,))
                result = cursor.fetchone()

                if result:
                    course_id = result[0]
                else:
                    # 2. 없으면 새로 생성 (기본 수강생 99명)
                    # print(f"🆕 새 강의 추가: {course_name} ({course_code})")
                    cursor.execute('''
                                   INSERT INTO courses (name, course_code, total_students)
                                   VALUES (?, ?, 99)
                                   ''', (course_name, course_code))
                    course_id = cursor.lastrowid

                # 3. 리뷰 데이터 삽입
                cursor.execute('''
                               INSERT INTO course_reviews (course_id, content)
                               VALUES (?, ?)
                               ''', (course_id, review_content))

                count += 1

                if count % 100 == 0:
                    print(f"   ...{count}개 처리 중")

        conn.commit()
        print(f"✅ 총 {count}개의 리뷰 처리 완료!")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


if __name__ == "__main__":
    import_data()
