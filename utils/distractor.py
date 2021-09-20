from loguru import logger
import torch
from config import MAX_CONTEXT_LENGTH,MAX_LENGTH,MAX_ANSWER_LENGTH,MAX_QUESTION_LENGTH
import wget
from nlgeval import NLGEval
from transformers import RobertaTokenizer, AutoTokenizer
from transformers import RobertaForMultipleChoice,AutoModelForSeq2SeqLM
from torch.distributions import Categorical
import itertools as it
import nlp2go
from functools import lru_cache
import json
from qgg_utils.optim import GAOptimizer

def prepare_dis_model_input_ids(article,question,answer,tokenizer):
    context_input = tokenizer(
        article,
        max_length=MAX_CONTEXT_LENGTH,
        add_special_tokens=True,
        truncation=True
    )
    question_input = tokenizer(
        question,
        max_length=MAX_QUESTION_LENGTH,
        add_special_tokens=True,
        truncation=True
    )
    answer_input = tokenizer(
        answer,
        max_length=MAX_ANSWER_LENGTH,
        add_special_tokens=True,
        truncation=True
    )
    
    input_ids = context_input['input_ids'] + question_input['input_ids'][1:] + answer_input['input_ids'][1:]
    return torch.LongTensor([input_ids])

def selection():
    pass

class BartDistractorGeneration():
    def __init__(self):
        self.nlgeval = NLGEval(metrics_to_omit=['METEOR', 'EmbeddingAverageCosineSimilairty', 'SkipThoughtCS', 'VectorExtremaCosineSimilarity','GreedyMatchingScore', 'CIDEr'])
    
        #
        self.dg_models = [
            AutoModelForSeq2SeqLM.from_pretrained("voidful/bart-distractor-generation"),
            AutoModelForSeq2SeqLM.from_pretrained("voidful/bart-distractor-generation-pm"),
            AutoModelForSeq2SeqLM.from_pretrained("voidful/bart-distractor-generation-both"),
        ]

        self.dg_tokenizers = [
            AutoTokenizer.from_pretrained("voidful/bart-distractor-generation"),
            AutoTokenizer.from_pretrained("voidful/bart-distractor-generation-pm"),
            AutoTokenizer.from_pretrained("voidful/bart-distractor-generation-both"),
        ]

        for dg_model in self.dg_models:
            dg_model.to('cpu')

        #
        # self.tokenizer = RobertaTokenizer.from_pretrained("LIAMF-USP/roberta-large-finetuned-race")
        # self.model = RobertaForMultipleChoice.from_pretrained("LIAMF-USP/roberta-large-finetuned-race")
        # self.model.eval()
        # self.model.to(os.environ['BDG_CLF_DEVICE'])
    
    @lru_cache(maxsize=1000)
    def generate_distractor(self,context, question, answer, gen_quantity):
        if answer == '':
            logger.warning('answer is null')
            return []
        all_options = []
        for i,(dg_tokenizer,dg_model) in enumerate(zip(self.dg_tokenizers,self.dg_models)):
            d_input_ids = prepare_dis_model_input_ids(context,question,answer,dg_tokenizer)  # 如果文章過長進行重新裁切與處理
            out_ids = dg_model.generate(
                input_ids = d_input_ids.to(dg_model.device),
                num_beams = gen_quantity*3,
                length_penalty=0.9,
                num_beam_groups=gen_quantity,
                diversity_penalty=1.0,
                num_return_sequences = gen_quantity*2
            )
            for out_seq_ids in out_ids:
                option = dg_tokenizer.decode(out_seq_ids,skip_special_tokens=True)
                # logger.info(f"{i} {option}")
                all_options.append(option)
        # logger.info(all_options)
        # return all_options
        return self.selection(context,question,answer,all_options, gen_quantity)
    
    def selection(self,context, question, answer, all_options, gen_quantity):
        ga_optim = GAOptimizer(len(all_options),gen_quantity)
        return ga_optim.optimize(all_options,context)[:gen_quantity]
