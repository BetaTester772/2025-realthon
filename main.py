from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional
import os
from dotenv import load_dotenv
from openai import OpenAI

# ---------------------------------------------------------
# 0. Environment & OpenAI Setup
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=ENV_PATH)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = None

if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    print("✅ OpenAI Client initialized successfully.")
else:
    print("⚠ Warning: OPENAI_API_KEY not found.")

# ---------------------------------------------------------
# 1. Database Setup
# ---------------------------------------------------------
DB_PATH = os.path.join(BASE_DIR, "hackathon.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ---------------------------------------------------------
# 2. Database Models
# ---------------------------------------------------------
class StudentProfileModel(Base):
    __tablename__ = "student_profile"
    id = Column(Integer, primary_key=True, index=True)
    preferences = Column(String)

class OtherStudentScoreModel(Base):
    __tablename__ = "other_student_scores"
    id = Column(Integer, primary_key=True, index=True)
    evaluation_item_id = Column(Integer, index=True)
    score = Column(Float)

class CourseModel(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    course_code = Column(String, index=True)
    total_students = Column(Integer, default=99)

class EvaluationItemModel(Base):
    __tablename__ = "evaluation_items"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, index=True)
    name = Column(String)
    weight = Column(Integer)
    my_score = Column(Float, nullable=True)
    is_submitted = Column(Boolean, default=False)

class CourseReviewModel(Base):
    __tablename__ = "course_reviews"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, index=True)
    content = Column(String)

Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------
# 3. Pydantic Schemas
# ---------------------------------------------------------
# ... (기존 스키마 생략, 아래에 필요한 것들 포함됨) ...

class StudentProfileCreate(BaseModel):
    preferences: str
class StudentProfileResponse(BaseModel):
    id: int
    preferences: str
    class Config:
        from_attributes = True

class ScoreCreate(BaseModel):
    evaluation_item_id: int
    score: float
class ScoreResponse(ScoreCreate):
    id: int
    class Config:
        from_attributes = True

class CourseCreate(BaseModel):
    name: str
    course_code: str
    total_students: Optional[int] = 99
class CourseResponse(CourseCreate):
    id: int
    class Config:
        from_attributes = True

class EvaluationItemCreate(BaseModel):
    course_id: int
    name: str
    weight: int
    my_score: Optional[float] = None
    is_submitted: Optional[bool] = False
class EvaluationItemResponse(EvaluationItemCreate):
    id: int
    class Config:
        from_attributes = True

class CourseReviewCreate(BaseModel):
    course_id: int
    content: str
class CourseReviewResponse(CourseReviewCreate):
    id: int
    class Config:
        from_attributes = True

class HistogramPredictRequest(BaseModel):
    evaluation_item_id: int
    # total_students: Optional[int] = None
class HistogramPredictResponse(BaseModel):
    evaluation_item_id: int
    histogram: dict
    num_samples: int
    sample_scores: List[float]
    total_students: Optional[int] = None

# [AI Advice Single]
class ReviewAnalysisResponse(BaseModel):
    assignment_difficulty: int = Field(..., description="과제 난이도 (1~5)")
    exam_difficulty: int = Field(..., description="시험 난이도 (1~5)")
    summary: str = Field(..., description="시험/과제 공통 언급 요약")
    advice: str = Field(..., description="목표 성적 달성 조언")

# [AI Advice Whole Semester] (New)
class SemesterPlanItem(BaseModel):
    course_index: int = Field(..., description="입력된 과목 순서 (1부터 시작)")
    effort_percent: int = Field(..., description="투자해야 할 노력 비율 (0~100)")

class SemesterPlanResponse(BaseModel):
    courses: List[SemesterPlanItem]
    overall_advice: str = Field(..., description="전체 학기 운영을 위한 1-2문장 조언")

# ---------------------------------------------------------
# 4. FastAPI App & ML Setup
# ---------------------------------------------------------
app = FastAPI(title="Hackathon API", version="1.0.0")

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
)

ml_predictor = None
@app.on_event("startup")
async def startup_event():
    global ml_predictor
    try:
        from ML.model_loader import HistogramPredictor
        model_path = os.path.join(BASE_DIR, "ML", "best_model_nnj359uw.pt")
        ml_predictor = HistogramPredictor(model_path=model_path)
        print("✓ ML model loaded successfully")
    except:
        print("⚠ ML module skipped.")
        ml_predictor = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/dummy-histo")
async def get_dummy_histogram():
    return {"0-10": 5, "10-20": 15, "20-30": 25, "30-40": 10, "40-50": 8, "50-60": 12, "60-70": 7, "70-80": 3, "80-90": 1, "90-100": 0}

# ---------------------------------------------------------
# 5. Existing Endpoints
# ---------------------------------------------------------
# ... (기존 Student Profile, Courses, Items, Reviews, Scores API 생략 - 위 코드 유지) ...

@app.post("/student-profile", response_model=StudentProfileResponse, tags=["Student Profile"])
async def create_student_profile(profile: StudentProfileCreate, db: Session = Depends(get_db)):
    new_profile = StudentProfileModel(preferences=profile.preferences)
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile

@app.get("/student-profile", response_model=List[StudentProfileResponse], tags=["Student Profile"])
async def get_all_student_profiles(db: Session = Depends(get_db)):
    return db.query(StudentProfileModel).all()

@app.post("/courses", response_model=CourseResponse, tags=["Courses"])
async def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    new_course = CourseModel(**course.dict())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

@app.get("/courses", response_model=List[CourseResponse], tags=["Courses"])
async def get_all_courses(db: Session = Depends(get_db)):
    return db.query(CourseModel).all()

@app.post("/evaluation-items", response_model=EvaluationItemResponse, tags=["Evaluation Items"])
async def create_evaluation_item(item: EvaluationItemCreate, db: Session = Depends(get_db)):
    new_item = EvaluationItemModel(**item.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.get("/evaluation-items", response_model=List[EvaluationItemResponse], tags=["Evaluation Items"])
async def get_all_evaluation_items(db: Session = Depends(get_db)):
    return db.query(EvaluationItemModel).all()

@app.post("/course-reviews", response_model=CourseReviewResponse, tags=["Course Reviews"])
async def create_course_review(review: CourseReviewCreate, db: Session = Depends(get_db)):
    new_review = CourseReviewModel(**review.dict())
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review

@app.get("/course-reviews", response_model=List[CourseReviewResponse], tags=["Course Reviews"])
async def get_all_course_reviews(db: Session = Depends(get_db)):
    return db.query(CourseReviewModel).all()

@app.post("/other-student-scores", response_model=ScoreResponse, tags=["Other Student Scores"])
async def create_other_score(score_data: ScoreCreate, db: Session = Depends(get_db)):
    new_score = OtherStudentScoreModel(**score_data.dict())
    db.add(new_score)
    db.commit()
    db.refresh(new_score)
    return new_score

@app.get("/other-student-scores", response_model=List[ScoreResponse], tags=["Other Student Scores"])
async def get_other_scores(item_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(OtherStudentScoreModel)
    if item_id:
        query = query.filter(OtherStudentScoreModel.evaluation_item_id == item_id)
    return query.all()

@app.post("/predict-histogram", response_model=HistogramPredictResponse, tags=["ML Prediction"])
async def predict_histogram(request: HistogramPredictRequest, db: Session = Depends(get_db)):
    if ml_predictor is None:
        raise HTTPException(status_code=503, detail="ML model not loaded")
    scores = db.query(OtherStudentScoreModel).filter(OtherStudentScoreModel.evaluation_item_id == request.evaluation_item_id).all()
    if not scores:
        raise HTTPException(status_code=404, detail="No scores found")
    score_values = [s.score for s in scores]
    
    # total = request.total_students
    # if total is None:
    total = None
    item = db.query(EvaluationItemModel).filter(EvaluationItemModel.id == request.evaluation_item_id).first()
    if item:
        course = db.query(CourseModel).filter(CourseModel.id == item.course_id).first()
        if course and course.total_students:
            total = course.total_students
    if total is None: total = 99

    try:
        histogram = ml_predictor.predict(score_values, total_students=total)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

    return HistogramPredictResponse(
        evaluation_item_id=request.evaluation_item_id,
        histogram=histogram,
        num_samples=len(score_values),
        sample_scores=score_values,
        total_students=total
    )

@app.get("/courses/{course_id}/advice", response_model=ReviewAnalysisResponse, tags=["AI Advice"])
async def get_course_advice(course_id: int, objective_grade: str, db: Session = Depends(get_db)):
    if not openai_client:
        raise HTTPException(status_code=503, detail="OpenAI API Key missing")
    reviews = db.query(CourseReviewModel).filter(CourseReviewModel.course_id == course_id).all()
    if not reviews:
        raise HTTPException(status_code=404, detail="리뷰 데이터가 없습니다.")
    course_reviews_str = "\n".join([f"- {r.content}" for r in reviews])
    
    try:
        completion = openai_client.beta.chat.completions.parse(
            model="gpt-5-mini", 
            messages=[
                {"role": "system", "content": "당신은 강의평 분석 전문가입니다."},
                {"role": "user", "content": f"목표성적: {objective_grade}\n리뷰:\n{course_reviews_str}\n위 내용을 바탕으로 분석해주세요."}
            ],
            response_format=ReviewAnalysisResponse,
        )
        return completion.choices[0].message.parsed
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Error: {str(e)}")

# ---------------------------------------------------------
# 6. [New] Whole Semester Strategy Endpoint
# ---------------------------------------------------------
@app.get("/semester-advice", response_model=SemesterPlanResponse, tags=["AI Advice"])
async def get_semester_advice(
    course_ids: List[int] = Query(..., description="수강할 과목 ID 리스트 (예: 1, 2, 3)"),
    target_grades: List[str] = Query(..., description="각 과목의 목표 성적 (예: A+, A, B+)"),
    db: Session = Depends(get_db)
):
    """
    여러 과목의 리뷰를 종합하여 전체 학기 공부 비중(%)과 전략을 짜줍니다.
    - course_ids의 순서와 target_grades의 순서는 일치해야 합니다.
    - 예: /semester-advice?course_ids=1&course_ids=2&target_grades=A+&target_grades=B0
    """
    if not openai_client:
        raise HTTPException(status_code=503, detail="OpenAI API Key missing")

    if len(course_ids) != len(target_grades):
        raise HTTPException(status_code=400, detail="과목 수와 목표 성적 수가 일치해야 합니다.")

    # 1. 각 과목의 리뷰 데이터 수집
    combined_reviews_text = ""
    
    for idx, (cid, grade) in enumerate(zip(course_ids, target_grades)):
        course = db.query(CourseModel).filter(CourseModel.id == cid).first()
        if not course:
            continue # 없는 강의는 패스하거나 에러 처리
            
        reviews = db.query(CourseReviewModel).filter(CourseReviewModel.course_id == cid).all()
        review_texts = "\n".join([f"- {r.content}" for r in reviews]) if reviews else "리뷰 없음"
        
        combined_reviews_text += f"\n[과목 {idx+1}: {course.name} (목표: {grade})]\n{review_texts}\n"

    if not combined_reviews_text:
        raise HTTPException(status_code=404, detail="선택한 과목들에 대한 리뷰 데이터가 없습니다.")

    # 2. OpenAI 프롬프트 호출
    try:
        completion = openai_client.beta.chat.completions.parse(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 대학생의 전체 학기 학습 계획을 설계하는 전략가입니다."
                },
                {
                    "role": "user",
                    "content": f"""
                    다음은 이번 학기 수강할 과목들의 리뷰와 목표 성적입니다.
                    
                    {combined_reviews_text}
                    
                    위 내용을 바탕으로 다음을 JSON으로 분석해주세요:
                    1. 각 과목별 투자해야 할 노력 비율(effort_percent, 총합 100이 되도록).
                       - 과목 순서(course_index)는 1, 2, 3... 순으로 매칭할 것.
                    2. 전체 학기에 대한 1~2문장의 핵심 조언(overall_advice).
                    """
                }
            ],
            response_format=SemesterPlanResponse,
        )
        
        return completion.choices[0].message.parsed

    except Exception as e:
        print(f"OpenAI Error: {str(e)}")
        raise HTTPException(status_code=500, detail="AI 분석 중 오류가 발생했습니다.")