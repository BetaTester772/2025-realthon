"""
데이터베이스 초기화 모듈.

이 모듈은 SQLite 데이터베이스를 초기화하고 필요한 테이블 스키마를 생성합니다.
기존 데이터베이스 파일이 있는 경우 삭제 후 새로 생성합니다.

테이블 구조:
    - student_profile: 학생 프로필 정보 (id, preferences)
    - courses: 강의 정보 (id, name, course_code, total_students)
    - evaluation_items: 평가 항목 (id, course_id, name, weight, my_score, is_submitted)
    - other_student_scores: 다른 학생들의 점수 데이터 (id, evaluation_item_id, score)
    - course_reviews: 강의 수강평 (id, course_id, content)

사용법:
    python init_db.py
"""

import sqlite3
import os

# 데이터베이스 파일명 상수
DB_NAME = "hackathon.db"


def init_db() -> None:
    """
    데이터베이스를 초기화하고 테이블 스키마를 생성합니다.

    이 함수는 다음 작업을 수행합니다:
        1. 기존 데이터베이스 파일이 있으면 삭제
        2. 새로운 SQLite 데이터베이스 연결 생성
        3. 외래 키 제약조건 활성화
        4. 5개의 테이블 생성 (student_profile, courses, evaluation_items,
           other_student_scores, course_reviews)

    Note:
        이 함수를 실행하면 기존 데이터가 모두 삭제됩니다.
        프로덕션 환경에서는 주의해서 사용해야 합니다.
    """
    # 기존 파일 삭제 (스키마 변경 적용)
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"🗑️ 기존 {DB_NAME} 파일을 삭제했습니다.")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    print("🛠️ 테이블 생성을 시작합니다...")

    # 1. Student Profile
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS student_profile
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY,
                       preferences
                       TEXT
                   )
                   ''')

    # 2. Courses (★ 수정됨: 학수번호만 남김)
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS courses
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY,
                       name
                       TEXT
                       NOT
                       NULL,   -- 강의명 (예: 운영체제)
                       course_code
                       TEXT,   -- 학수번호 (예: COSE341) - 식별자
                       total_students
                       INTEGER -- 수강생 수
                   )
                   ''')

    # 3. Evaluation Items
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS evaluation_items
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY,
                       course_id
                       INTEGER
                       NOT
                       NULL,
                       name
                       TEXT
                       NOT
                       NULL,
                       weight
                       INTEGER
                       NOT
                       NULL,
                       my_score
                       REAL
                       DEFAULT
                       NULL,
                       is_submitted
                       BOOLEAN
                       DEFAULT
                       0,
                       FOREIGN
                       KEY
                   (
                       course_id
                   ) REFERENCES courses
                   (
                       id
                   ) ON DELETE CASCADE
                       )
                   ''')

    # 4. Other Student Scores
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS other_student_scores
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY,
                       evaluation_item_id
                       INTEGER
                       NOT
                       NULL,
                       score
                       REAL
                       NOT
                       NULL,
                       FOREIGN
                       KEY
                   (
                       evaluation_item_id
                   ) REFERENCES evaluation_items
                   (
                       id
                   ) ON DELETE CASCADE
                       )
                   ''')

    # 5. Course Reviews
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS course_reviews
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY,
                       course_id
                       INTEGER
                       NOT
                       NULL,
                       content
                       TEXT,
                       FOREIGN
                       KEY
                   (
                       course_id
                   ) REFERENCES courses
                   (
                       id
                   ) ON DELETE CASCADE
                       )
                   ''')

    conn.commit()
    conn.close()
    print(f"🎉 '{DB_NAME}' 파일 생성 및 스키마 업데이트 완료! (심플 버전)")


if __name__ == "__main__":
    init_db()
