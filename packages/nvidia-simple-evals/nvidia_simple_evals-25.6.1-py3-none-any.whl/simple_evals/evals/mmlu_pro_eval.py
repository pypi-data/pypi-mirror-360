"""
MMLU-Pro: A More Robust and Challenging Multi-Task Language Understanding Benchmark
https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro
"""

import random
import re

import pandas as pd
from datasets import load_dataset
import simple_evals.common as common
from simple_evals.common import (
    HTML_JINJA,
    normalize_extracted_answer,
    normalize_response,
)
from simple_evals.simple_evals_types import Eval, EvalResult, SamplerBase, SingleEvalResult, SeedGenerator


PROMPT_TEMPLATE = '''
Answer the following multiple choice question. The last line of your response should be in the following format: 'Answer: A/B/C/D/E/F/G/H/I/J' (e.g. 'Answer: A'). 

{Question}

A) {A}
B) {B}
C) {C}
D) {D}
E) {E}
F) {F}
G) {G}
H) {H}
I) {I}
J) {J}
'''


class MMLUProEval(Eval):
    def __init__(
        self, 
        num_examples: int | None = None,
        num_threads: int = 10,
        first_n: int | float | None = None,
        cache_dir: str = "cache",
        seed_generator: SeedGenerator | None = None,
        downsampling_ratio: float | None = None
    ):
        super().__init__(seed_generator=seed_generator)
        
        # Load MMLU-Pro dataset
        df = load_dataset("TIGER-Lab/MMLU-Pro", split="test").to_pandas()
        
        # Standardize column names
        df.columns = df.columns.str.capitalize()
        
        # Handle 10 choices (A-J)
        choices = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        df[choices] = pd.DataFrame(df['Options'].tolist(), index=df.index)
        
        examples = [row.to_dict() for _, row in df.iterrows()]

         # Validate parameters
        if num_examples is not None and downsampling_ratio is not None:
            raise ValueError("Cannot specify both num_examples and downsampling_ratio")
        if downsampling_ratio is not None and not 0 < downsampling_ratio <= 1:
            raise ValueError("downsampling_ratio must be between 0 and 1")
        
        if downsampling_ratio is not None:
            num_examples = int(len(examples) * downsampling_ratio)

        if num_examples:
            # Use seed_generator for consistent sampling
            base_seed = self.seed_generator.get_seed(0)
            rng = random.Random(base_seed)
            examples = rng.sample(examples, num_examples)
            
        self.examples = examples
        self.num_threads = num_threads
        self.first_n = first_n
        self.cache_dir = cache_dir

    async def __call__(self, sampler: SamplerBase) -> EvalResult:
        async def fn(row: dict, index: int):
            prompt_messages = [
                sampler._pack_message(
                    content=PROMPT_TEMPLATE.format(**row), role="user"
                )
            ]
            completion_seed = self.seed_generator.get_seed(index)
            response_text = normalize_response(await sampler(prompt_messages, seed=completion_seed))
            
            extracted_answer = None
            # https://artificialanalysis.ai/methodology/intelligence-benchmarking
            regex = "(?i)[\*\_]{0,2}Answer[\*\_]{0,2}\s*:[\s\*\_]{0,2}\s*([A-Z])(?![a-zA-Z0-9])"
            match = re.search(regex, response_text)
            if match:
                extracted_answer = normalize_extracted_answer(match.group(1))
                    
            score = 1.0 if extracted_answer == row["Answer"] else 0.0
            html = common.jinja_env.from_string(HTML_JINJA).render(
                prompt_messages=prompt_messages,
                next_message=dict(content=response_text, role="assistant"),
                score=score,
                correct_answer=row["Answer"],
                extracted_answer=extracted_answer,
            )
            convo = prompt_messages + [dict(content=response_text, role="assistant")]
            category = row["Category"].lower()
            return SingleEvalResult(
                html=html, score=score, metrics={category: score}, convo=convo
            )

        results = await common.map_with_progress(
            fn, 
            self.examples, 
            num_threads=self.num_threads, 
            cache_dir=self.cache_dir, 
            first_n=self.first_n
        )
        return common.aggregate_results(results, add_macro=True, task_name="mmlu_pro")
