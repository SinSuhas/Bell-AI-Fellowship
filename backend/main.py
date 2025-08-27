from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Optional
import uvicorn

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./habits.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Habit(Base):
    __tablename__ = "habits"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    created_date = Column(Date, default=date.today)

class HabitEntry(Base):
    __tablename__ = "habit_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, index=True)
    date = Column(Date, index=True)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class HabitCreate(BaseModel):
    name: str
    description: Optional[str] = ""

class HabitResponse(BaseModel):
    id: int
    name: str
    description: str
    created_date: date
    
    class Config:
        from_attributes = True

class HabitEntryCreate(BaseModel):
    habit_id: int
    date: date
    completed: bool

class HabitEntryResponse(BaseModel):
    id: int
    habit_id: int
    date: date
    completed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class HabitWithStatus(BaseModel):
    id: int
    name: str
    description: str
    completed_today: bool

# FastAPI app
app = FastAPI(title="Habit Rabbit API", description="Simple daily habit tracker API")

# Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API Routes
@app.get("/")
def read_root():
    return {"message": "Welcome to Habit Rabbit API! 🐰"}

@app.post("/habits/", response_model=HabitResponse)
def create_habit(habit: HabitCreate, db: Session = Depends(get_db)):
    db_habit = Habit(name=habit.name, description=habit.description)
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return db_habit

@app.get("/habits/", response_model=List[HabitResponse])
def get_habits(db: Session = Depends(get_db)):
    habits = db.query(Habit).all()
    return habits

@app.get("/habits/today", response_model=List[HabitWithStatus])
def get_habits_today(db: Session = Depends(get_db)):
    today = date.today()
    habits = db.query(Habit).all()
    result = []
    
    for habit in habits:
        entry = db.query(HabitEntry).filter(
            HabitEntry.habit_id == habit.id,
            HabitEntry.date == today
        ).first()
        
        result.append(HabitWithStatus(
            id=habit.id,
            name=habit.name,
            description=habit.description,
            completed_today=entry.completed if entry else False
        ))
    
    return result

@app.post("/habits/{habit_id}/complete")
def toggle_habit_completion(habit_id: int, db: Session = Depends(get_db)):
    today = date.today()
    
    # Check if habit exists
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    # Check if entry exists for today
    entry = db.query(HabitEntry).filter(
        HabitEntry.habit_id == habit_id,
        HabitEntry.date == today
    ).first()
    
    if entry:
        # Toggle completion status
        entry.completed = not entry.completed
    else:
        # Create new entry as completed
        entry = HabitEntry(habit_id=habit_id, date=today, completed=True)
        db.add(entry)
    
    db.commit()
    return {"message": f"Habit {'completed' if entry.completed else 'uncompleted'} for today"}

@app.delete("/habits/{habit_id}")
def delete_habit(habit_id: int, db: Session = Depends(get_db)):
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    # Delete all entries for this habit
    db.query(HabitEntry).filter(HabitEntry.habit_id == habit_id).delete()
    # Delete the habit
    db.delete(habit)
    db.commit()
    return {"message": "Habit deleted successfully"}

@app.get("/habits/{habit_id}/history")
def get_habit_history(habit_id: int, db: Session = Depends(get_db)):
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    entries = db.query(HabitEntry).filter(HabitEntry.habit_id == habit_id).order_by(HabitEntry.date.desc()).limit(30).all()
    return entries

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
