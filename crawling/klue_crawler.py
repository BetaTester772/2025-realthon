"""
KLUE (고려대학교 강의평가 사이트) 크롤러 모듈.

이 모듈은 Selenium을 사용하여 KLUE 웹사이트에서 강의 수강평을 크롤링합니다.
로그인 후 지정된 강의들의 수강평을 수집하여 CSV 파일로 저장합니다.

주요 기능:
    - KLUE 웹사이트 로그인
    - 학수번호 + 교수명으로 강의 검색
    - 무한 스크롤 페이지에서 모든 수강평 수집
    - CSV 파일로 결과 저장

출력 파일:
    klue_reviews_multi.csv
    컬럼: course_code, professor, lecture_id, year, semester, review

사용법:
    python crawling/klue_crawler.py

환경 변수:
    KLUE_ID: KLUE 로그인 아이디 (선택, 없으면 입력 프롬프트)
    KLUE_PW: KLUE 로그인 비밀번호 (선택, 없으면 입력 프롬프트)

의존성:
    - selenium
    - webdriver-manager
    - Chrome 브라우저
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from getpass import getpass
import time
import os
import csv
import re


# =============================================================================
# 브라우저 드라이버 설정
# =============================================================================

def create_driver() -> webdriver.Chrome:
    """
    Chrome WebDriver 인스턴스를 생성합니다.

    자동으로 ChromeDriver를 다운로드하고 설치한 후,
    최대화된 브라우저 창으로 드라이버를 반환합니다.

    Returns:
        webdriver.Chrome: 설정된 Chrome WebDriver 인스턴스
    """
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    driver.implicitly_wait(5)
    return driver


# =============================================================================
# 유틸리티 함수
# =============================================================================

def scroll_to_bottom(driver: webdriver.Chrome, pause: float = 1.0, max_rounds: int = 50) -> None:
    """
    무한 스크롤 페이지에서 끝까지 스크롤합니다.

    페이지 높이가 더 이상 변하지 않을 때까지 반복적으로
    페이지 하단으로 스크롤하여 동적 콘텐츠를 모두 로드합니다.

    Args:
        driver: Selenium WebDriver 인스턴스
        pause: 각 스크롤 후 대기 시간 (초)
        max_rounds: 최대 스크롤 반복 횟수

    Note:
        3회 연속 페이지 높이 변화가 없으면 스크롤을 종료합니다.
    """
    last_height = driver.execute_script("return document.body.scrollHeight")
    stable_rounds = 0

    for i in range(max_rounds):
        # 맨 아래로 스크롤
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause)

        new_height = driver.execute_script("return document.body.scrollHeight")
        print(f"[DEBUG] loop {i}, height: {new_height}")

        if new_height == last_height:
            stable_rounds += 1
        else:
            stable_rounds = 0
            last_height = new_height

        # 몇 번 연속 높이 변화가 없으면 종료
        if stable_rounds >= 3:
            break

# =============================================================================
# 크롤링 함수
# =============================================================================

def get_lecture_reviews(driver: webdriver.Chrome, lecture_id: int) -> list[str]:
    """
    특정 강의 페이지에서 모든 수강평을 수집합니다.

    Args:
        driver: Selenium WebDriver 인스턴스
        lecture_id: KLUE 강의 ID (URL의 /lectures/{id} 부분)

    Returns:
        list[str]: 수강평 텍스트 리스트
    """
    wait = WebDriverWait(driver, 10)

    url = f"https://klue.kr/lectures/{lecture_id}"
    driver.get(url)
    scroll_to_bottom(driver)

    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.white-space_pre-wrap")
        )
    )

    review_divs = driver.find_elements(By.CSS_SELECTOR, "div.white-space_pre-wrap")

    reviews: list[str] = []
    for div in review_divs:
        text = div.text.strip()
        if text:
            reviews.append(text)

    return reviews


def parse_year_sem(header_text: str) -> tuple[int | None, int | None]:
    """
    강의 헤더 텍스트에서 연도와 학기 정보를 추출합니다.

    Args:
        header_text: 강의 정보 텍스트 (예: "2025년 1학기 - COSE341(01)")

    Returns:
        tuple: (연도, 학기) - 파싱 실패 시 (None, None)

    Example:
        >>> parse_year_sem("2025년 1학기 - COSE341(01)")
        (2025, 1)
    """
    m = re.search(r"(\d{4})년\s*([0-9])학기", header_text)
    if not m:
        return None, None
    year = int(m.group(1))
    semester = int(m.group(2))
    return year, semester


def get_lectures_by_prof(driver: webdriver.Chrome, search_query: str, professor_name: str) -> list[dict]:
    """
    검색 결과 페이지에서 특정 교수의 강의 목록을 수집합니다.

    학수번호로 검색한 결과에서 특정 교수의 강의만 필터링하여
    강의 ID, 연도, 학기 정보를 추출합니다.

    Args:
        driver: Selenium WebDriver 인스턴스
        search_query: 검색어 (학수번호, 예: "COSE341")
        professor_name: 교수명 (예: "유혁")

    Returns:
        list[dict]: 강의 정보 리스트
            각 항목: {"id": int, "year": int|None, "semester": int|None}
    """
    wait = WebDriverWait(driver, 10)

    url = f"https://klue.kr/search?query={search_query}&sort=year_term"
    driver.get(url)

    # 무한 스크롤이라 아래로 몇 번 내려서 로딩시키기 (필요하면 횟수 조정)
    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)

    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href^="/lectures/"]'))
    )

    lecture_links = driver.find_elements(By.CSS_SELECTOR, 'a[href^="/lectures/"]')

    lectures = []
    seen_ids = set()

    for a in lecture_links:
        # 교수님 이름 있는 p 태그 찾기
        try:
            prof_el = a.find_element(
                By.XPATH, './/p[contains(text(),"교수님")]'
            )
            prof_text = prof_el.text.strip()
        except Exception:
            continue

        if professor_name not in prof_text:
            continue

        # 과목 정보(연도/학기 포함된 부분)는 보통 카드의 첫 번째 p에 있음
        try:
            p_tags = a.find_elements(By.TAG_NAME, "p")
            header_text = p_tags[0].text.strip() if p_tags else ""
        except Exception:
            header_text = ""

        year, semester = parse_year_sem(header_text)

        # lecture id 추출
        href = a.get_attribute("href")
        if not href:
            continue
        if href.startswith("/"):
            href_full = "https://klue.kr" + href
        else:
            href_full = href

        lec_str = href_full.rstrip("/").split("/")[-1]
        try:
            lec_id = int(lec_str)
        except ValueError:
            continue

        if lec_id in seen_ids:
            continue
        seen_ids.add(lec_id)

        lectures.append(
            {
                "id": lec_id,
                "year": year,
                "semester": semester,
            }
        )

    return lectures


# =============================================================================
# 메인 실행 코드
# =============================================================================

# 로그인 정보 (환경 변수 또는 사용자 입력)
USER_ID = os.getenv("KLUE_ID") or input("KLUE 아이디: ")
USER_PW = os.getenv("KLUE_PW") or getpass("KLUE 비밀번호: ")

# WebDriver 초기화
driver = create_driver()
wait = WebDriverWait(driver, 10)

# 크롤링할 강의 목록 설정
# 각 항목: search_query (학수번호), professor_name (교수명)
TARGET_LECTURES = [
    {"search_query": "COSE111", "professor_name": "유용재"},   # 전산수학I
    {"search_query": "COSE341", "professor_name": "유혁"},     # 운영체제
    {"search_query": "COSE389", "professor_name": "이문영"},   # 기업가정신과리더십
]

try:
    # =========================================================================
    # 1단계: KLUE 웹사이트 로그인
    # =========================================================================
    driver.get("https://klue.kr/")

    login_link = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="/login"]'))
    )
    login_link.click()

    id_input = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'input[placeholder="아이디"]')
        )
    )
    pw_input = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="비밀번호"]')

    id_input.clear()
    id_input.send_keys(USER_ID)
    pw_input.clear()
    pw_input.send_keys(USER_PW)

    login_btn = driver.find_element(By.XPATH, '//button[contains(text(), "로그인")]')
    login_btn.click()

    time.sleep(5)
    print("로그인 후 URL:", driver.current_url)

    # =========================================================================
    # 2단계: 강의별 수강평 크롤링
    # =========================================================================
    rows = []  # 수집된 모든 수강평을 저장할 리스트

    for target in TARGET_LECTURES:
        search_query = target["search_query"]
        professor_name = target["professor_name"]
        print(f"\n=== {search_query} / {professor_name} 크롤링 시작 ===")

        # (1) 해당 학부번호 + 교수명으로 강의 목록 가져오기
        lecture_meta_list = get_lectures_by_prof(driver, search_query, professor_name)
        print("찾은 강의들:", lecture_meta_list)

        # (2) 각 강의별 후기 크롤링
        for meta in lecture_meta_list:
            lec_id = meta["id"]
            year = meta["year"]
            semester = meta["semester"]

            reviews = get_lecture_reviews(driver, lec_id)
            print(
                f"강의 {lec_id} ({year}년 {semester}학기, {search_query}, {professor_name}) 후기 {len(reviews)}개"
            )

            for rv in reviews:
                rows.append(
                    {
                        "course_code": search_query,     # 학부번호(과목번호)
                        "professor": professor_name,     # 교수명
                        "lecture_id": lec_id,            # klue 강의 ID
                        "year": year,
                        "semester": semester,
                        "review": rv,
                    }
                )

    # =========================================================================
    # 3단계: CSV 파일로 결과 저장
    # =========================================================================
    output_file = "klue_reviews_multi.csv"
    with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "course_code",
                "professor",
                "lecture_id",
                "year",
                "semester",
                "review",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nCSV 저장 완료: {output_file} (총 {len(rows)}행)")

finally:
    driver.quit()
