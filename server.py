from os import truncate
from typing import Optional,List,Any
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import BartTokenizerFast, BartForConditionalGeneration
import torch
import re
from qgg_utils.optim import GAOptimizer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

# server setting
origins = [    
    "http://localhost",
    "http://localhost:3000",
]
app = FastAPI()
app.mount("/react", StaticFiles(directory="react/build"), name="react")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# utils
def feedback_generation(qgg, input_ids, feedback_times = 3):
        outputs = []
        device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')        
        input_ids = input_ids.squeeze(0).tolist()        
        
        for i in range(feedback_times):
            gened_text = qgg.tokenizer.bos_token * (len(outputs)+1)
            gened_ids = qgg.tokenizer(gened_text,add_special_tokens=False)['input_ids']            
            input_ids = gened_ids + input_ids
            input_ids = input_ids[:MAX_LENGTH]
            
            sample_outputs = qgg.model.generate(
                input_ids = torch.LongTensor(input_ids).unsqueeze(0).to(device),
                attention_mask=torch.LongTensor([1]*len(input_ids)).unsqueeze(0).to(device),
                max_length=50,
                early_stopping=True,
                temperature=1.0,
                do_sample=True,
                top_p=0.9,
                top_k=10,
                num_beams=1,
                no_repeat_ngram_size=5,
                num_return_sequences=1,
            )
            sample_output = sample_outputs[0]        
            decode_question = qgg.tokenizer.decode(sample_output, skip_special_tokens=False)
            decode_question = re.sub(re.escape(qgg.tokenizer.pad_token),'',decode_question)
            decode_question = re.sub(re.escape(qgg.tokenizer.eos_token),'',decode_question)
            if qgg.tokenizer.bos_token is not None:
                decode_question = re.sub(re.escape(qgg.tokenizer.bos_token),'',decode_question)
            decode_question = decode_question.strip()
            decode_question = decode_question.replace("[Q:]","")            
            outputs.append(decode_question)
        return outputs

# data model
class GenerationOrder(BaseModel):
    context: str
    question_group_size: Optional[int] = 5
    candidate_pool_size: Optional[int] = 10

class QuestionGroupGenerator(BaseModel):
    model: Any
    tokenizer: Any
    optim: Any

# nn model setting
qgg=QuestionGroupGenerator(
        model=BartForConditionalGeneration.from_pretrained("p208p2002/qmst-qgg"),
        tokenizer=BartTokenizerFast.from_pretrained("p208p2002/qmst-qgg")
    )
MAX_LENGTH=512

# router
@app.get("/", response_class=HTMLResponse)
async def root():
    with open("react/build/index.html","r",encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.post("/generate")
async def generate(order:GenerationOrder):
    context = order.context
    question_group_size = order.question_group_size
    candidate_pool_size = order.candidate_pool_size
    qgg_optim = GAOptimizer(candidate_pool_size,question_group_size)
    
    # 
    if candidate_pool_size < question_group_size:
        return {'message':'`candidate_pool_size` must bigger than `question_group_size`'},400    
    if candidate_pool_size > 20:
        return {'message':'`candidate_pool_size` must smaller than 20'},400
    if question_group_size > 10:
        return {'message':'`question_group_size` must smaller than 10'},400
    
    input_ids = qgg.tokenizer(
                    context,
                    max_length=MAX_LENGTH,
                    truncation=True,
                    add_special_tokens=False,
                    return_tensors='pt'
                )['input_ids']
    candidate_questions = feedback_generation(qgg=qgg,input_ids=input_ids,feedback_times=order.candidate_pool_size)
    question_group = qgg_optim.optimize(candidate_questions,context)
    return {'question_group':question_group}


