from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./shifa_demo.db')
connect_args = {'check_same_thread': False} if DATABASE_URL.startswith('sqlite') else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Department(Base):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True, index=True)
    name_ar = Column(String(160), nullable=False)
    name_en = Column(String(160), default='')

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(240), nullable=False)
    department = Column(String(160), default='')
    status = Column(String(40), default='جديدة')
    notes = Column(Text, default='')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Knowledge(Base):
    __tablename__ = 'knowledge'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(240), nullable=False)
    body = Column(Text, nullable=False)
    category = Column(String(120), default='عام')

Base.metadata.create_all(bind=engine)
app = FastAPI(title='SHIFA | شفاء - Demo API', version='0.1.0', description='نسخة تجريبية أولية - لا تستخدم بيانات مرضى حقيقية')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

class DepartmentIn(BaseModel):
    name_ar: str = Field(min_length=1, max_length=160)
    name_en: str = ''
class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=240)
    department: str = ''
    status: str = 'جديدة'
    notes: str = ''
class KnowledgeIn(BaseModel):
    title: str
    body: str
    category: str = 'عام'

@app.get('/')
def home(): return {'system':'SHIFA | شفاء','mode':'DEMO','message':'مرحباً بك في النسخة التجريبية','warning':'لا تدخل بيانات مرضى أو معلومات شخصية حقيقية.'}
@app.get('/health')
def health(): return {'status':'ok'}
@app.get('/departments')
def list_departments(db: Session = Depends(get_db)):
    return db.query(Department).order_by(Department.id).all()
@app.post('/departments')
def add_department(item: DepartmentIn, db: Session = Depends(get_db)):
    row=Department(**item.model_dump()); db.add(row); db.commit(); db.refresh(row); return row
@app.get('/tasks')
def list_tasks(db: Session = Depends(get_db)):
    return db.query(Task).order_by(Task.id.desc()).all()
@app.post('/tasks')
def add_task(item: TaskIn, db: Session = Depends(get_db)):
    row=Task(**item.model_dump()); db.add(row); db.commit(); db.refresh(row); return row
@app.patch('/tasks/{task_id}')
def update_task(task_id: int, status: str, db: Session = Depends(get_db)):
    row=db.get(Task, task_id)
    if not row: raise HTTPException(404,'Task not found')
    row.status=status; db.commit(); db.refresh(row); return row
@app.get('/knowledge')
def list_knowledge(db: Session = Depends(get_db)):
    return db.query(Knowledge).order_by(Knowledge.id.desc()).all()
@app.post('/knowledge')
def add_knowledge(item: KnowledgeIn, db: Session = Depends(get_db)):
    row=Knowledge(**item.model_dump()); db.add(row); db.commit(); db.refresh(row); return row
