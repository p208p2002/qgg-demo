from pydantic import BaseModel
from typing import Optional,List,Any

# data model
class GenerationOrder(BaseModel):
    context: str
    question_group_size: Optional[int] = 5
    candidate_pool_size: Optional[int] = 10

class QuestionGroupGenerator(BaseModel):
    model: Any
    tokenizer: Any
    optim: Any

class QuestionAndAnswer(BaseModel):
    question:str
    answer:str

class DistractorOrder(BaseModel):
    context: str
    question_and_answers: List[QuestionAndAnswer]
