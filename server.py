from fastapi import FastAPI
from transformers import BartTokenizerFast, BartForConditionalGeneration, AutoTokenizer
import torch
from qgg_utils.optim import GAOptimizer
from qgg_utils.scorer import CoverageScorer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from loguru import logger
from utils.data_model import *
from utils import feedback_generation
from utils.distractor import BartDistractorGeneration
from config import MAX_LENGTH,MAX_CONTEXT_LENGTH

# server setting
origins = [    
    "*",
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

# nn model setting
device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')        
qgg=QuestionGroupGenerator(
        model=BartForConditionalGeneration.from_pretrained("p208p2002/qmst-qgg"),
        tokenizer=BartTokenizerFast.from_pretrained("p208p2002/qmst-qgg")
    )
qgg.model.to(device)

#
bdg = BartDistractorGeneration()

# router
@app.get("/", response_class=HTMLResponse)
async def root():
    with open("react/build/index.html","r",encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.post("/generate-question-group")
async def generate(order:GenerationOrder):
    # return {'question_group':[
    #             'Harry Potter is a series of seven fantasy novels written by   _ .',
    #             'Who is Voldemort?',
    #             'How does the story begin?'
    #         ]}

    context = order.context
    question_group_size = order.question_group_size
    candidate_pool_size = order.candidate_pool_size
    
    # 
    if candidate_pool_size < question_group_size:
        return {'message':'`candidate_pool_size` must bigger than `question_group_size`'},400    
    if candidate_pool_size > 20:
        return {'message':'`candidate_pool_size` must smaller than 20'},400
    if question_group_size > 10:
        return {'message':'`question_group_size` must smaller than 10'},400
    
    tokenize_result = qgg.tokenizer.batch_encode_plus(
                    [context],
                    stride=MAX_LENGTH - int(MAX_LENGTH*0.7),
                    max_length=MAX_LENGTH,
                    truncation=True,
                    add_special_tokens=False,
                    return_overflowing_tokens=True,
                    return_length=True,
                )
    candidate_questions = []
    logger.info(f"Size of tokenize_result.input_ids:{len(tokenize_result.input_ids)}")
    
    if len(tokenize_result.input_ids)>=10:
        logger.warning(f"Force cut tokenize_result.input_ids({len(tokenize_result.input_ids)}) to 10, it's too big")
        tokenize_result.input_ids = tokenize_result.input_ids[:10]
        
    for input_ids in tokenize_result.input_ids:
        candidate_questions += feedback_generation(qgg=qgg,input_ids=input_ids,feedback_times=order.candidate_pool_size)
    logger.info(f"Size of candidate_questions:{len(candidate_questions)}")

    while len(candidate_questions) > question_group_size:
        qgg_optim = GAOptimizer(len(candidate_questions),question_group_size)
        candidate_questions = qgg_optim.optimize(candidate_questions,context)
    return {'question_group':candidate_questions}

@app.post("/generate-distractor")
async def generate(order:DistractorOrder):
    tokenizer = AutoTokenizer.from_pretrained("voidful/bart-distractor-generation")
    tokenize_result = tokenizer.batch_encode_plus(
        [order.context],
        stride=MAX_CONTEXT_LENGTH - int(MAX_CONTEXT_LENGTH*0.7),
        max_length=MAX_CONTEXT_LENGTH,
        truncation=True,
        add_special_tokens=False,
        return_overflowing_tokens=True,
        return_length=True,
    )
    # logger.debug(tokenize_result)

    # 由於內文有長度限制；計算問句最匹配的內文段落
    keyword_coverage_scorer = CoverageScorer()
    cqas = []
    for question_and_answer in order.question_and_answers:
        question = question_and_answer.question
        answer = question_and_answer.answer
        score = 0.0
        paragraph = tokenizer.decode(tokenize_result.input_ids[0])
        for input_ids in tokenize_result.input_ids:
            _paragraph = tokenizer.decode(input_ids)
            _score = keyword_coverage_scorer._compute_coverage_score([question],_paragraph)
            # logger.debug(f"Q:{question} A:{answer} score:{score}")

            if _score > score:
                score = _score
                paragraph = _paragraph

        cqas.append({
            'context':paragraph,
            'question':question,
            'answer':answer
        })
    
    outs = []
    for cqa in cqas:
        options = bdg.generate_distractor(
            context=cqa['context'],
            question=cqa['question'],
            answer=cqa['answer'],
            gen_quantity=3
        )
        logger.info(f"Q:{cqa['question']} A:{cqa['answer']} O:{options}")
        outs.append({
            "_context":cqa['context'],
            "options":options,
            "question":cqa['question'],
            "answer":cqa['answer']
        })
    return {
        "distractors":outs
    }

