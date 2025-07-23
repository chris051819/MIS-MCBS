from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, validator
from typing import List, Optional
import uuid
from datetime import datetime, date, timedelta
from enum import Enum
import json

# Custom JSON encoder for date objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class StudentStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    GRADUATED = "graduated"
    SUSPENDED = "suspended"

class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class GradeLevel(str, Enum):
    KG = "Kindergarten"
    GRADE_1 = "Grade 1"
    GRADE_2 = "Grade 2"
    GRADE_3 = "Grade 3"
    GRADE_4 = "Grade 4"
    GRADE_5 = "Grade 5"
    GRADE_6 = "Grade 6"
    GRADE_7 = "Grade 7"
    GRADE_8 = "Grade 8"
    GRADE_9 = "Grade 9"
    GRADE_10 = "Grade 10"
    GRADE_11 = "Grade 11"
    GRADE_12 = "Grade 12"

# Models
class Student(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: date
    gender: GenderEnum
    grade_level: GradeLevel
    status: StudentStatus = StudentStatus.ACTIVE
    address: Optional[str] = None
    parent_name: Optional[str] = None
    parent_email: Optional[str] = None
    parent_phone: Optional[str] = None
    enrollment_date: date = Field(default_factory=date.today)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('email', pre=True, always=True)
    def validate_email(cls, v):
        if v and v.strip() and '@' not in v:
            raise ValueError('Invalid email format')
        return v
    
    def dict(self, **kwargs):
        """Override dict method to handle date serialization"""
        data = super().dict(**kwargs)
        # Convert date objects to strings for MongoDB
        if isinstance(data.get('date_of_birth'), date):
            data['date_of_birth'] = data['date_of_birth'].isoformat()
        if isinstance(data.get('enrollment_date'), date):
            data['enrollment_date'] = data['enrollment_date'].isoformat()
        return data

class StudentCreate(BaseModel):
    student_id: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: date
    gender: GenderEnum
    grade_level: GradeLevel
    address: Optional[str] = None
    parent_name: Optional[str] = None
    parent_email: Optional[str] = None
    parent_phone: Optional[str] = None

class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    grade_level: Optional[GradeLevel] = None
    status: Optional[StudentStatus] = None
    address: Optional[str] = None
    parent_name: Optional[str] = None
    parent_email: Optional[str] = None
    parent_phone: Optional[str] = None

class Teacher(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    teacher_id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    subject_specialization: Optional[str] = None
    hire_date: date = Field(default_factory=date.today)
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TeacherCreate(BaseModel):
    teacher_id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    subject_specialization: Optional[str] = None

class Course(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    course_code: str
    course_name: str
    description: Optional[str] = None
    credit_hours: Optional[int] = None
    grade_levels: List[GradeLevel] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CourseCreate(BaseModel):
    course_code: str
    course_name: str
    description: Optional[str] = None
    credit_hours: Optional[int] = None
    grade_levels: List[GradeLevel] = []

class DashboardStats(BaseModel):
    total_students: int
    active_students: int
    total_teachers: int
    total_courses: int
    students_by_grade: dict
    recent_enrollments: int

# Original status check models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# Dashboard and Statistics
@api_router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    # Count total students
    total_students = await db.students.count_documents({})
    active_students = await db.students.count_documents({"status": "active"})
    total_teachers = await db.teachers.count_documents({})
    total_courses = await db.courses.count_documents({})
    
    # Students by grade
    pipeline = [
        {"$group": {"_id": "$grade_level", "count": {"$sum": 1}}}
    ]
    grade_counts = await db.students.aggregate(pipeline).to_list(None)
    students_by_grade = {item["_id"]: item["count"] for item in grade_counts}
    
    # Recent enrollments (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_enrollments = await db.students.count_documents({
        "enrollment_date": {"$gte": thirty_days_ago.date()}
    })
    
    return DashboardStats(
        total_students=total_students,
        active_students=active_students,
        total_teachers=total_teachers,
        total_courses=total_courses,
        students_by_grade=students_by_grade,
        recent_enrollments=recent_enrollments
    )

# Student CRUD Operations
@api_router.post("/students", response_model=Student)
async def create_student(student: StudentCreate):
    # Check if student_id already exists
    existing = await db.students.find_one({"student_id": student.student_id})
    if existing:
        raise HTTPException(status_code=400, detail="Student ID already exists")
    
    student_dict = student.dict()
    student_obj = Student(**student_dict)
    
    await db.students.insert_one(student_obj.dict())
    return student_obj

@api_router.get("/students", response_model=List[Student])
async def get_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    grade_level: Optional[GradeLevel] = Query(None),
    status: Optional[StudentStatus] = Query(None)
):
    query = {}
    
    if search:
        query["$or"] = [
            {"first_name": {"$regex": search, "$options": "i"}},
            {"last_name": {"$regex": search, "$options": "i"}},
            {"student_id": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]
    
    if grade_level:
        query["grade_level"] = grade_level
    
    if status:
        query["status"] = status
    
    students = await db.students.find(query).skip(skip).limit(limit).sort("created_at", -1).to_list(limit)
    # Convert string dates back to date objects
    result = []
    for student_data in students:
        if isinstance(student_data.get('date_of_birth'), str):
            student_data['date_of_birth'] = datetime.fromisoformat(student_data['date_of_birth']).date()
        if isinstance(student_data.get('enrollment_date'), str):
            student_data['enrollment_date'] = datetime.fromisoformat(student_data['enrollment_date']).date()
        result.append(Student(**student_data))
    return result

@api_router.get("/students/count")
async def get_students_count(
    search: Optional[str] = Query(None),
    grade_level: Optional[GradeLevel] = Query(None),
    status: Optional[StudentStatus] = Query(None)
):
    query = {}
    
    if search:
        query["$or"] = [
            {"first_name": {"$regex": search, "$options": "i"}},
            {"last_name": {"$regex": search, "$options": "i"}},
            {"student_id": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]
    
    if grade_level:
        query["grade_level"] = grade_level
    
    if status:
        query["status"] = status
    
    count = await db.students.count_documents(query)
    return {"count": count}

@api_router.get("/students/{student_id}", response_model=Student)
async def get_student(student_id: str):
    student = await db.students.find_one({"id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return Student(**student)

@api_router.put("/students/{student_id}", response_model=Student)
async def update_student(student_id: str, student_update: StudentUpdate):
    student = await db.students.find_one({"id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    update_data = student_update.dict(exclude_unset=True)
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await db.students.update_one({"id": student_id}, {"$set": update_data})
    
    updated_student = await db.students.find_one({"id": student_id})
    return Student(**updated_student)

@api_router.delete("/students/{student_id}")
async def delete_student(student_id: str):
    result = await db.students.delete_one({"id": student_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student deleted successfully"}

# Teacher CRUD Operations
@api_router.post("/teachers", response_model=Teacher)
async def create_teacher(teacher: TeacherCreate):
    existing = await db.teachers.find_one({"teacher_id": teacher.teacher_id})
    if existing:
        raise HTTPException(status_code=400, detail="Teacher ID already exists")
    
    teacher_dict = teacher.dict()
    teacher_obj = Teacher(**teacher_dict)
    
    await db.teachers.insert_one(teacher_obj.dict())
    return teacher_obj

@api_router.get("/teachers", response_model=List[Teacher])
async def get_teachers():
    teachers = await db.teachers.find().sort("created_at", -1).to_list(100)
    return [Teacher(**teacher) for teacher in teachers]

@api_router.get("/teachers/{teacher_id}", response_model=Teacher)
async def get_teacher(teacher_id: str):
    teacher = await db.teachers.find_one({"id": teacher_id})
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return Teacher(**teacher)

# Course CRUD Operations
@api_router.post("/courses", response_model=Course)
async def create_course(course: CourseCreate):
    existing = await db.courses.find_one({"course_code": course.course_code})
    if existing:
        raise HTTPException(status_code=400, detail="Course code already exists")
    
    course_dict = course.dict()
    course_obj = Course(**course_dict)
    
    await db.courses.insert_one(course_obj.dict())
    return course_obj

@api_router.get("/courses", response_model=List[Course])
async def get_courses():
    courses = await db.courses.find().sort("created_at", -1).to_list(100)
    return [Course(**course) for course in courses]

# Original routes
@api_router.get("/")
async def root():
    return {"message": "School Management Information System API"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()