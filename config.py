MAX_LENGTH=512
MAX_CONTEXT_LENGTH=MAX_LENGTH-52
MAX_QUESTION_LENGTH=20
MAX_ANSWER_LENGTH=16
assert MAX_LENGTH>=(MAX_QUESTION_LENGTH+MAX_ANSWER_LENGTH)