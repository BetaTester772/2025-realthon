"""
학기 전체 학습 계획 생성 프롬프트 테스트 모듈.

이 모듈은 OpenAI API를 사용하여 여러 과목의 수강평을 분석하고
학기 전체 학습 계획(노력 배분 비율)과 종합 조언을 생성합니다.

기능:
    - CSV 파일에서 수강평 데이터 로드
    - OpenAI GPT 모델을 통한 학습 계획 생성
    - JSON Schema를 사용한 구조화된 응답 생성

출력 형식 (JSON):
    {
        "courses": [
            {"course_index": 1, "effort_percent": 40},
            {"course_index": 2, "effort_percent": 30},
            {"course_index": 3, "effort_percent": 30}
        ],
        "overall_advice": "전체 학기 운영을 위한 조언..."
    }

사용법:
    python prompt/whole_advice_prompt.py

환경 변수:
    OPENAI_API_KEY: OpenAI API 키 (필수)
"""

from openai import OpenAI
import os
from dotenv import load_dotenv
import pandas as pd

# 환경 변수 로드 (.env 파일에서 OPENAI_API_KEY 읽기)
load_dotenv()

# =============================================================================
# OpenAI 클라이언트 초기화
# =============================================================================
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# =============================================================================
# 수강평 데이터 로드
# =============================================================================
# CSV 파일에서 강의 ID와 수강평 내용을 읽어옴
df = pd.read_csv("../crawling/klue_reviews_multi.csv")
reviews = df[["lecture_id", "review"]].to_dict(orient="records")

# =============================================================================
# 수강평 데이터 전처리
# =============================================================================
# 수강평 데이터를 딕셔너리 형태로 변환
course_reviews = []
for review in reviews:
    course_reviews.append(
            {
                    "course_id" : review["lecture_id"],  # 강의 ID
                    "content"   : review["review"],       # 수강평 본문
                    "generosity": 0,                      # 채점 관대함 (미사용)
                    "id"        : len(course_reviews) + 1,  # 순차적 ID
            }
    )

# 수강평 내용만 추출하여 줄바꿈으로 연결
course_reviews_str = "\n".join(
        [f"{review['content']}" for review in course_reviews]
)

# 각 과목의 목표 성적 (순서대로 과목 1, 2, 3에 해당)
objective_grade = ["A+", "A", "B+"]

# =============================================================================
# OpenAI 응답 JSON Schema 정의
# =============================================================================
# 구조화된 응답을 위한 JSON Schema
# - courses: 각 과목별 노력 투자 비율 (합계 100)
# - overall_advice: 전체 학기 조언 (1-2문장)
semester_plan_schema = {
        "type"                : "object",
        "properties"          : {
                "courses"       : {
                        "type" : "array",
                        "items": {
                                "type"                : "object",
                                "properties"          : {
                                        "course_index"  : {
                                                "type"       : "integer",
                                                "minimum"    : 1,
                                                "maximum"    : 3,
                                                "description": "1, 2, 3 중 하나"
                                        },
                                        "effort_percent": {
                                                "type"       : "integer",
                                                "minimum"    : 0,
                                                "maximum"    : 100,
                                                "description": "해당 과목에 투자할 비율 (0~100 정수)"
                                        }
                                },
                                "required"            : ["course_index", "effort_percent"],
                                "additionalProperties": False
                        }
                },
                "overall_advice": {
                        "type"       : "string",
                        "description": "세 과목 전체를 고려한 1~2문장의 전반적인 조언"
                }
        },
        "required"            : ["courses", "overall_advice"],
        "additionalProperties": False
}

# =============================================================================
# OpenAI API 호출
# =============================================================================
# GPT 모델에 수강평과 목표 성적을 전달하여 학습 계획 생성
response = client.responses.create(
        model="gpt-5-mini",
        input=f"""
    너는 학습 계획을 설계하는 조교이다.

    반드시 아래 JSON Schema를 만족하는 JSON 한 개만 출력해야 한다.
    - JSON 이외의 텍스트(설명, 마크다운 등)는 절대 출력하지 마라.

    과목 3개에 대한 리뷰가 주어지며,
    목표 성적은 {objective_grade[0]}, {objective_grade[1]}, {objective_grade[2]} 이다.
    (하지만 목표 성적은 JSON 출력 형식에는 포함하지 않는다.)

    아래 규칙에 따라 JSON을 생성하라.

    [규칙]
    1) 각 과목에 대해 effort_percent(0~100 정수)를 정하라.
    2) effort_percent들의 합은 반드시 100이 되어야 한다.
    3) courses 배열의 course_index는 1, 2, 3 중 하나로 고정한다.
    4) 전체 학기에 대한 조언(overall_advice)은 1~2문장으로만 작성한다.

    --------- 수강평 시작 ---------
    {course_reviews_str}
    --------- 수강평 끝 ---------
    """,
        text={
                "verbosity": "low",
                "format"   : {
                        "type"  : "json_schema",
                        "name"  : "semester_plan",
                        "schema": semester_plan_schema,  # ← 여기!
                },
        },
        reasoning={"effort": "low"},
)

# response = client.responses.create(
#     model="gpt-5-mini",
#     input=f"""
#     목표성적: {objective_grade[0]}, {objective_grade[1]}, {objective_grade[2]}
#     이건 과목 3개의 이전 수강자들의 강의평 입니다. 각 강의평은 과목 ID와 함께 주어집니다.
#     목표성적은 각 과목의 목표성적을 의미합니다. 
#     목표성적에 따라 각 과목에 투자해야 할 비중을 전체 100% 비율로 정리해주세요. 
#     각 과목의 수강평과 목표 성적을 종합하여 해당 학기 수강에 대한 전반적인 조언을 1-2문장으로 정리해주세요. 
#     이 때 조언은 과목별로 나눠서 주지 말고 전반적인 조언으로 주세요.
#     {course_reviews_str}
#     """,
#     text={
#         "verbosity": "low",
#     },
#     reasoning={"effort": "low"},
# )

print(response.output_text)
