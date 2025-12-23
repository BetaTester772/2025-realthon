# 똑똑한 학습 전략성적키트

> Smart Learning Strategy & Grade Toolkit

학생 성적 분포를 예측하는 머신러닝 기반 API 시스템

## 프로젝트 개요

소수의 학생 점수 샘플로부터 전체 학급의 성적 분포를 예측하는 FastAPI 기반 백엔드 시스템입니다. SetTransformer 아키텍처를 활용한 딥러닝 모델로 히스토그램 예측을 수행합니다.

## 주요 기능

- **성적 히스토그램 예측**: 샘플 점수로부터 전체 학급의 성적 분포 예측
- **누적 히스토그램 생성**: 과목별 평가 항목들의 가중치를 고려한 누적 성적 분포
- **과목 및 평가 항목 관리**: 과목, 과제, 시험 등의 평가 항목 CRUD
- **학생 프로필 관리**: 학생 선호도 및 프로필 정보 관리
- **OpenAI API 통합**: AI 기반 학습 조언 제공 (과목별 학습 전략, 학기 계획)
- **Redis 캐시**: OpenAI API 응답 캐싱으로 빠른 응답 속도 제공

## 기술 스택

### Backend

- **FastAPI** 0.121.3+ - 고성능 웹 프레임워크
- **SQLAlchemy** 2.0.0+ - ORM 및 데이터베이스 관리
- **Pydantic** 2.12.4+ - 데이터 검증 및 스키마 정의
- **Uvicorn** 0.38.0+ - ASGI 서버
- **Redis** 5.0.0+ - 캐시 서버 (OpenAI API 응답 캐싱)

### Machine Learning

- **PyTorch** 2.9.1+ - 딥러닝 프레임워크
- **SetTransformer** - 집합 기반 예측 모델 아키텍처
- **NumPy** 2.3.5+ - 수치 연산
- **Weights & Biases** - 실험 추적 및 모델 관리

### Development Tools

- **Jupyter** - 모델 개발 및 실험
- **Matplotlib** - 데이터 시각화
- **OpenAI API** - AI 기능 통합

## 프로젝트 구조

```
2025-realthon/
├── main.py                    # FastAPI 애플리케이션 메인
├── hackathon.db               # SQLite 데이터베이스
├── pyproject.toml             # 프로젝트 의존성 관리
├── Dockerfile                 # Docker 이미지 빌드 설정
├── docker-compose.yml         # Docker Compose 서비스 구성
├── Caddyfile                  # Caddy 리버스 프록시 설정
├── ML/                        # 머신러닝 모듈
│   ├── model_loader.py        # 모델 아키텍처 및 예측기
│   └── best_model_nnj359uw.pt # 학습된 모델 체크포인트
├── crawling/                  # 데이터 수집 모듈
└── init_db.py                 # 데이터베이스 초기화
```

## 설치 및 실행

### 요구사항

- Python 3.11
- uv (권장) 또는 pip

### 설치

```bash
# 저장소 클론
git clone https://github.com/BetaTester772/2025-realthon.git
cd 2025-realthon

# uv를 사용한 의존성 설치 (권장)
uv sync

# 또는 pip 사용
pip install -e .
```

### 환경 설정

`.env` 파일을 생성하고 필요한 환경 변수를 설정합니다:

```bash
# OpenAI API 설정 (필수)
OPENAI_API_KEY=your_api_key_here

# Redis 캐시 설정 (선택, 기본값 사용 가능)
REDIS_HOST=localhost    # 기본값: localhost
REDIS_PORT=6379         # 기본값: 6379
REDIS_DB=0              # 기본값: 0
CACHE_TTL=3600          # 캐시 유효 시간(초), 기본값: 3600 (1시간)
```

**Redis 설치 및 실행 (선택사항)**

Redis가 설치되어 있지 않으면 캐시가 비활성화되며, API는 정상 작동합니다.

```bash
# macOS (Homebrew)
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# Windows (WSL 사용 권장)
```

### 데이터베이스 초기화

```bash
python init_db.py
```

### 서버 실행

#### 방법 1: Docker Compose (권장)

```bash
# .env 파일에 OPENAI_API_KEY 설정 필요
# Docker Compose로 모든 서비스 시작 (FastAPI + Redis + Caddy)
docker compose up -d

# 로그 확인
docker compose logs -f

# 서비스 재시작 (코드 변경 후 즉시 적용)
docker compose restart

# 특정 서비스만 재시작
docker compose restart app

# 이미지 재빌드 후 재시작 (Dockerfile 변경 시)
docker compose up -d --build

# 서비스 중지
docker compose down

# 볼륨까지 삭제 (Redis 데이터 포함)
docker compose down -v
```

서비스 구성:
- **FastAPI App**: 백엔드 API 서버
- **Redis**: 캐시 서버 (OpenAI API 응답 캐싱)
- **Caddy**: 리버스 프록시 및 SSL 지원

API 문서는 `http://localhost/docs` (Caddy를 통한 접근) 또는 `http://localhost:8000/docs` (직접 접근)에서 확인할 수 있습니다.

#### 방법 2: 로컬 실행

```bash
# Redis 수동 실행 필요 (선택사항)
# macOS: brew services start redis
# Ubuntu: sudo systemctl start redis

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API 문서는 `http://localhost:8000/docs`에서 확인할 수 있습니다.

## API 엔드포인트

자세한 API 명세는 서버 실행 후 `/docs` 엔드포인트에서 Swagger UI를 통해 확인할 수 있습니다.

### System

- `GET /health` - 서버 상태 확인
    - 반환: `{"status": "healthy"}`

- `GET /dummy-histo` - 테스트용 더미 히스토그램 데이터
    - 개발/디버깅 용도의 샘플 히스토그램 반환

### ML Prediction

- `GET /predict-histogram` - 평가 항목별 성적 분포 예측
    - Query Parameters: `evaluation_item_id` (필수)
    - 기능: SetTransformer 모델을 사용하여 샘플 점수로부터 전체 학급의 성적 분포를 예측
    - 반환:
        - `histogram`: 10개 구간(0-10, 10-20, ..., 90-100)의 성적 분포
        - `num_samples`: 예측에 사용된 샘플 수
        - `sample_scores`: 사용된 샘플 점수 리스트
        - `total_students`: 전체 학생 수
        - `my_score`: 사용자의 점수 (있는 경우)
        - `my_percentile`: 사용자의 백분위 (my_score가 있는 경우)
        - `statistics`: 히스토그램 통계 정보 (평균, 중앙값, 최고/최저, 상위/하위 10%)

- `GET /courses/{course_id}/cumulative-histogram` - 과목별 누적 성적 분포
    - Path Parameters: `course_id` (필수)
    - 기능: 과목의 모든 평가 항목(과제, 시험 등)을 가중치에 따라 합산하여 최종 성적 분포 예측
    - 반환:
        - `cumulative_histogram`: 가중 평균 누적 히스토그램
        - `total_weight`: 전체 가중치 합계
        - `evaluation_items`: 각 평가 항목별 히스토그램과 가중치 정보
        - `my_cumulative_score`: 사용자의 가중 평균 점수 (my_score가 있는 경우)
        - `my_percentile`: 사용자의 백분위 (my_cumulative_score가 있는 경우)
        - `statistics`: 누적 히스토그램 통계 정보

### Student Profile

- `GET /student-profile` - 학생 프로필 조회
    - 반환: ID 1번 학생의 프로필 정보 (preferences)

- `PUT /student-profile` - 학생 프로필 업데이트
    - Request Body: `{"preferences": "학생 선호도 및 특성"}`
    - 기능: ID 1번 학생의 프로필 정보를 업데이트 (없으면 생성)
    - 반환: 업데이트된 프로필 정보

### Course Management

- `GET /courses` - 전체 과목 목록 조회
    - 반환: 모든 과목 정보 리스트

- `POST /courses` - 새 과목 생성
    - Request Body:
        ```json
        {
          "name": "과목명",
          "course_code": "과목 코드",
          "total_students": 99  // 선택사항, 기본값 99
        }
        ```
    - 반환: 생성된 과목 정보

### Evaluation Items

- `GET /evaluation-items` - 전체 평가 항목 목록 조회
    - 반환: 모든 평가 항목 정보 리스트

- `POST /evaluation-items` - 새 평가 항목 생성
    - Request Body:
        ```json
        {
          "course_id": 1,
          "name": "평가 항목명",
          "weight": 30,  // 가중치 (%)
          "my_score": 85.5,  // 선택사항
          "is_submitted": false  // 선택사항, 기본값 false
        }
        ```
    - 반환: 생성된 평가 항목 정보

### Course Reviews

- `GET /course-reviews` - 전체 과목 수강평 목록 조회
    - 반환: 모든 수강평 리스트

- `POST /course-reviews` - 새 수강평 생성
    - Request Body:
        ```json
        {
          "course_id": 1,
          "content": "수강평 내용"
        }
        ```
    - 반환: 생성된 수강평 정보
    - **참고**: 새 수강평 추가 시 해당 과목의 모든 AI 조언 캐시가 자동으로 무효화됩니다.

### Other Student Scores

- `GET /other-student-scores` - 다른 학생들의 점수 조회
    - Query Parameters: `item_id` (선택사항, 평가 항목 ID로 필터링)
    - 반환: 학생 점수 데이터 리스트

- `POST /other-student-scores` - 새 학생 점수 데이터 생성
    - Request Body:
        ```json
        {
          "evaluation_item_id": 1,
          "score": 82.5
        }
        ```
    - 반환: 생성된 점수 데이터

### AI Advice (OpenAI API)

AI 조언 기능은 OpenAI API를 사용하며, Redis 캐싱을 통해 동일한 요청에 대한 응답 속도를 향상시킵니다.

- `GET /courses/{course_id}/advice` - 과목별 학습 조언
    - Path Parameters: `course_id` (필수)
    - Query Parameters: `objective_grade` (필수, 목표 성적 예: "A+", "A0", "B+")
    - 기능:
        - 과목의 수강평을 분석하여 과제 및 시험 난이도 평가
        - 목표 성적 달성을 위한 학습 전략 제공
        - 학생 프로필의 선호도 정보를 고려한 맞춤형 조언
    - 반환:
        ```json
        {
          "assignment_difficulty": 4,  // 1-5 척도
          "exam_difficulty": 3,  // 1-5 척도
          "summary": "시험/과제 공통 언급 요약",
          "advice": "목표 성적 달성 전략 조언"
        }
        ```
    - 캐시: `course_id` + `objective_grade` 조합으로 캐싱 (TTL: 1시간)

- `GET /semester-advice` - 학기 전체 학습 계획
    - Query Parameters:
        - `course_ids`: 수강할 과목 ID 리스트 (예: `?course_ids=1&course_ids=2&course_ids=3`)
        - `target_grades`: 각 과목의 목표 성적 리스트 (예: `?target_grades=A+&target_grades=B0&target_grades=A0`)
    - 기능:
        - 여러 과목의 수강평을 종합 분석
        - 각 과목별 노력 배분 비율(%) 계산
        - 전체 학기 학습 전략 제공
        - 학생 프로필의 선호도 정보를 고려한 맞춤형 계획
    - 반환:
        ```json
        {
          "courses": [
            {"course_index": 1, "effort_percent": 35},
            {"course_index": 2, "effort_percent": 40},
            {"course_index": 3, "effort_percent": 25}
          ],
          "overall_advice": "전체 학기 운영 조언"
        }
        ```
    - 캐시: `course_ids` + `target_grades` 조합으로 캐싱 (TTL: 1시간)

### Cache Management

- `DELETE /cache/clear` - Redis 캐시 무효화
    - Query Parameters: `pattern` (선택사항, 기본값: "*")
    - 예시:
        - `/cache/clear` - 모든 캐시 삭제
        - `/cache/clear?pattern=course_advice:*` - 과목 조언 캐시만 삭제
        - `/cache/clear?pattern=semester_advice:*` - 학기 조언 캐시만 삭제
    - 반환: `{"message": "Cache cleared for pattern: ..."}`

## ML 모델 아키텍처

### FlexibleHistogramPredictor (SetTransformer-inspired ISAB-style Encoder)

프로젝트는 **SetTransformer에서 영감을 받은** 딥러닝 모델을 사용하여 소수의 샘플 점수(예: 10개)로부터 전체 학급의 성적 분포(30명 학생의 10개 구간 히스토그램)를 예측합니다. 이 모델은 ISAB(Induced Set Attention Block) 스타일의 인코더와 간소화된 mean pooling 디코더를 결합한 아키텍처입니다.

#### 모델 구조

```
Input (샘플 점수)
  → 전처리 (정렬, 0-1 정규화)
  → Input Projection (1 → hidden_dim)
  → SetTransformer-style Encoder (ISAB-style: Inducing Points 기반)
  → Mean Pooling (집합 특성 집약)
  → MLP Decoder (hidden_dim → 10 bins)
  → Softmax
Output (히스토그램 확률 분포)
```

#### 핵심 컴포넌트

1. **입력 전처리**
    - **정렬**: 입력 샘플 점수를 오름차순으로 정렬하여 순서를 표준화
    - **정규화**: 0-1 범위로 정규화 (점수/100)
    - 목적: 동일한 점수 집합에 대해 일관된 입력 표현 제공

2. **MultiheadAttentionBlock (MAB)**
    - Multi-head Cross-Attention with residual connections
    - Layer Normalization
    - Feed-Forward Network (dim → 4×dim → dim)
    - Dropout regularization

3. **SetTransformerEncoder (ISAB-style)**
    - **Inducing Points (I)**: 학습 가능한 latent representations (기본 16개)
    - ISAB 구조로 집합 원소 간 관계를 효율적으로 인코딩
    - 두 단계 attention (ISAB 방식):
        1. H = MAB(I, X): Inducing Points가 입력 집합 X를 attend → H 생성
        2. Output = MAB(X, H): 입력 집합 X가 H를 attend → 인코딩된 표현
    - **참고**: 전체 SetTransformer의 PMA(Pooling by Multihead Attention)는 사용하지 않음

4. **집약(Aggregation)**
    - Mean Pooling: 인코딩된 집합 요소들의 평균을 계산
    - PMA 대신 mean pooling을 사용하여 경량화 및 프로토타이핑 효율성 확보
    - 집합 전체의 특성을 단일 벡터로 요약

5. **디코더**
    - 단순 MLP + Softmax
    - 집약된 특징 벡터를 10개 구간의 확률 분포로 변환

#### 하이퍼파라미터

| 파라미터           | 기본값 | 설명                |
|----------------|-----|-------------------|
| `hidden_dim`   | 64  | 임베딩 차원            |
| `num_heads`    | 4   | Attention head 수  |
| `num_inducers` | 16  | Inducing Points 수 |
| `dropout`      | 0.1 | Dropout 비율        |
| `num_bins`     | 10  | 히스토그램 구간 수        |

#### 입력/출력

- **입력**: 가변 길이 점수 샘플 (0-100 범위, 정규화 후 0-1)
- **출력**: 10개 구간의 확률 분포 (0-10, 10-20, ..., 90-100)
    - 확률값 (0-1) 또는 학생 수 (total_students 파라미터 지정 시)

#### 학습 데이터

합성 데이터 생성 기반 학습:

- **4가지 난이도 타입**:
    - `easy`: 평균 75-90점, 표준편차 5-10
    - `normal`: 평균 60-80점, 표준편차 8-15
    - `hard`: 평균 40-65점, 표준편차 8-15
    - `bimodal`: 이중 정규분포 (40-60점 그룹 + 70-90점 그룹)
- 각 클래스당 30명 학생 기준
- **중요**: 이 모델은 합성 데이터로 학습되었으며, 실제 환경에서의 일반화 성능은 제한적일 수 있습니다.

### 아키텍처 설계 근거

본 프로젝트에서 SetTransformer-inspired 아키텍처를 선택한 이유는 다음과 같습니다:

#### 1. 입력 표준화와 집합 표현
- 샘플 점수는 **점수 집합**으로 취급되며, 전처리에서 정렬하여 순서를 표준화
- 예: [75, 82, 68]과 [68, 75, 82]는 모두 [68, 75, 82]로 변환되어 동일한 예측 결과 생성
- SetTransformer 아키텍처는 정렬된 집합에서도 유효:
  - Attention 메커니즘은 원소 간 관계(패턴, 분산, 클러스터링)를 학습
  - Mean pooling은 집합 전체의 특성을 하나의 벡터로 집약
  - 모델은 "정렬된 점수 시퀀스"의 통계적 패턴을 히스토그램으로 매핑하도록 학습

#### 2. 효율적인 전역 상호작용
- **Inducing Points (IP)** 메커니즘을 통해 집합 전체의 패턴을 효율적으로 포착
- 작은 집합(10개 샘플)에서도 아키텍처 일관성을 유지하고 확장 가능성 확보
- ISAB-style attention은 O(nm) 복잡도로 전역 상호작용을 근사 (n=집합 크기, m=inducing points)

#### 3. 경량화된 디코더
- **Mean Pooling vs PMA**: 해커톤/프로토타이핑 환경에서 빠른 구현과 효율성을 위해 PMA 대신 mean pooling 선택
- Mean pooling은 집합의 특성을 단순 평균으로 요약하며 계산 비용이 낮음
- MLP 디코더로 히스토그램 확률 분포를 직접 예측

#### 4. 이론적 배경
- **Deep Sets** (Zaheer et al., 2017): 집합 함수의 순서 불변성을 위한 이론적 기반
- **Attention Is All You Need** (Vaswani et al., 2017): Multi-head attention의 표현력
- **Set Transformer** (Lee et al., 2019): 집합 데이터를 위한 효율적인 attention 메커니즘

### 학습 및 평가 지표

#### 학습 손실 함수 (Training Loss)

- **MSE Loss** (Mean Squared Error)
- 예측 확률 분포와 실제 히스토그램 간의 평균 제곱 오차
- 히스토그램의 각 구간 확률을 직접 최적화
- **선택 이유**:
  - 미분 가능하여 역전파에 적합
  - 계산 효율적 (빠른 학습)
  - 안정적인 수렴

#### 평가 지표 (Evaluation Metrics)

학습 완료 후 모델 성능은 다음 세 가지 지표로 측정됩니다:

1. **MSE** (Mean Squared Error)
    - 예측 히스토그램과 실제 히스토그램의 평균 제곱 오차
    - 각 구간의 확률값 차이를 제곱하여 평균
    - **특징**: 개별 구간의 정확도를 측정하나, 분포의 형태적 유사성은 포착하지 못함
    - **용도**: 학습 손실 및 기본 평가 지표
    - 낮을수록 정확한 예측

2. **JS Divergence** (Jensen-Shannon Divergence)
    - 두 확률 분포 간의 대칭적 거리 측정 (KL divergence의 대칭 버전)
    - **특징**: 분포 간의 전반적인 차이를 측정
    - **용도**: 분포의 전체적 유사도 평가
    - 0에 가까울수록 두 분포가 유사
    - 범위: [0, ln(2)] ≈ [0, 0.693]

3. **EMD** (Earth Mover's Distance = Wasserstein-1 거리)
    - 한 분포를 다른 분포로 변환하는데 필요한 최소 "작업량"
    - **특징**: 히스토그램의 형태적 유사성과 shift/translation을 잘 포착
    - **용도**: 히스토그램 예측의 실질적 성능 평가 (가장 적합한 지표)
    - 예: 실제 분포가 [0, 0, 5, 10, 8, 5, 2, 0, 0, 0]이고 예측이 [0, 5, 10, 8, 5, 2, 0, 0, 0, 0]일 때,
      - MSE/JS는 큰 차이를 보이지만, EMD는 단순히 한 구간 shift된 것으로 인식
    - 낮을수록 정확한 예측

**지표 역할 구분**:
- **MSE**: 학습 손실 + 빠른 평가
- **JS Divergence**: 정보 이론적 분포 유사도 평가
- **EMD**: 히스토그램 형태 평가 (실제 성능 측정에 가장 적합)

**참고**: JS Divergence와 EMD는 계산 비용과 복잡도로 인해 학습 손실로 사용하지 않고, 모델 평가 시에만 활용합니다.

### 모델 사용

```python
from ML.model_loader import HistogramPredictor

# 모델 로드
predictor = HistogramPredictor("ML/best_model_nnj359uw.pt")

# 샘플 점수로 예측
sample_scores = [75, 82, 68, 91, 77, 85, 73, 80, 88, 79]
histogram = predictor.predict(sample_scores, total_students=99)

# 결과: {"0-10": 0, "10-20": 2, ..., "90-100": 5}
```

## 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다.

```
MIT License

Copyright (c) 2025 2025-realthon contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 문의

이슈가 있거나 질문이 있으시면 GitHub Issues를 이용해주세요.

## 기여자

- **[BetaTester772](https://github.com/BetaTester772)**: Backend & AI/ML
- **[2022148084](https://github.com/2022148084)**: Backend
- **[garden-j](https://github.com/garden-j)**: Prompt Engineering
- **[claude](https://github.com/claude)**: Documentation

## References

### 학술 논문 (Academic Papers)

1. **Set Transformer: A Framework for Attention-based Permutation-Invariant Neural Networks**
   - Juho Lee, Yoonho Lee, Jungtaek Kim, Adam R. Kosiorek, Seungjin Choi, Yee Whye Teh
   - *Advances in Neural Information Processing Systems (NeurIPS) 32*, 2019
   - arXiv: [1810.00825](https://arxiv.org/abs/1810.00825)
   - 본 프로젝트의 ISAB-style encoder 아키텍처의 이론적 기반

2. **Attention Is All You Need**
   - Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser, Illia Polosukhin
   - *Advances in Neural Information Processing Systems (NeurIPS) 30*, 2017
   - Multi-head attention 메커니즘의 원본 논문

3. **Deep Sets**
   - Manzil Zaheer, Satwik Kottur, Siamak Ravanbakhsh, Barnabas Poczos, Ruslan Salakhutdinov, Alexander Smola
   - *Advances in Neural Information Processing Systems (NIPS) 30*, 2017
   - 집합 함수의 순서 불변성에 대한 이론적 기반 제공

### 기술 문서 및 도구

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/) - 백엔드 웹 프레임워크
- [PyTorch 공식 문서](https://pytorch.org/docs/) - 딥러닝 프레임워크
- [Weights & Biases](https://wandb.ai/) - 실험 추적 및 모델 관리
- [Redis 공식 문서](https://redis.io/docs/) - 캐시 서버

### 관련 개념

- **Wasserstein Distance / Earth Mover's Distance**: 확률 분포 간의 거리 측정 지표
- **Jensen-Shannon Divergence**: KL divergence의 대칭 버전으로, 분포 간 유사도 측정
- **Permutation Invariance**: 집합 데이터 처리를 위한 핵심 속성
