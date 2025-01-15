from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated
import models
from database import engine,SessionLocal
from sqlalchemy.orm import Session

#Creating an instance of FastApi
app = FastAPI()

#this creates all the tables in postgres
models.Base.metadata.create_all(bind=engine)

#creating structure of choices for the quiz application
class ChoiceBase(BaseModel):
    choice_text: str
    is_correct:bool

#creating structure of questions for the quiz

#the choices field will have the value which is are the instances of choiceBase
class QuestionBase(BaseModel):
    question_text:str
    choices: List[ChoiceBase]    

#making a connection with the database

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()    

#dependency injection
db_dependency = Annotated[Session,Depends(get_db)]

@app.post("/questions/")
async def create_questions(question:QuestionBase,db:db_dependency):

#defining a question, adding a question and then commiting it to save the results in the database and which will be retrievd b
    db_question = models.Questions(question_text = question.question_text)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    for choice in question.choices:
        db_choice   = models.Choices(choice_text = choice.choice_text, is_correct  = choice.is_correct,question_id = db_question.id)
        db.add(db_choice)
    db.commit()
    
@app.get("/questions/")
async def read_all_questions(db:db_dependency):
    result = db.query(models.Questions)
    if not result:
        raise HTTPException(status_code=404)

#api end point to retreive all the questions based on the question id
@app.get("/questions/{question_id}")
async def read_questions(question_id: int, db: db_dependency):
    result = db.query(models.Questions).filter(models.Questions.id == question_id).first()
    if not result:
        raise HTTPException(status_code=404,detail='Question is not found')
    return result

#api end point to retreive all the choices by providing the corresponding question id
@app.get("/choices/{question_id}")
async def read_choices(question_id: int, db: db_dependency):
    result = db.query(models.Choices).filter(models.Choices.question_id == question_id).all()
    if not result:
        raise HTTPException(status_code=404,detail='Choices is not found')
    return result