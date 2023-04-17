import re
import sqlite3
from pathlib import Path
import pandas as pd
from tqdm import tqdm

from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain

from prompts import *

pd.options.display.float_format = '{:.2f}'.format

class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


QUERY_FAILED = '<query_failed>'

def query_database(db_path, query, max_rows=15):

    try:
        with sqlite3.connect(path_to_db) as connection:
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchmany(max_rows)   # limit rows
            columns = tuple([x[0] for x in cursor.description])
            
            return pd.DataFrame(rows, columns=columns)
    
    except:
        return QUERY_FAILED


def get_schema(db_path, table_name):
    
    command = f"PRAGMA table_info('{table_name}')"
    
    with sqlite3.connect(path_to_db) as connection:
        cursor = connection.cursor()
        cursor.execute(command)
        rows = [row[1:3] for row in cursor.fetchall()]
        
    return rows

def extract_questions(input_string):
    pattern = r'^\d+\.\s+(.+?\?)'
    questions = re.findall(pattern, input_string, flags=re.MULTILINE)
    
    return questions

def extract_first_sql_query(input_string):
    pattern = r'(?:SELECT|WITH)(?:.|\n)*?(?=;|$)'
    query = re.search(pattern, input_string, flags=re.IGNORECASE)
    
    output_query = query.group(0) if query else None
    
    if output_query is None:
        return None
    return output_query + ';' if not output_query.endswith(';') else output_query


question_generator = LLMChain(
    llm=ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.4, max_tokens=2048), 
    prompt=generate_questions_prompt
)

query_generator = LLMChain(
    llm=ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.2, max_tokens=2048), 
    prompt=generate_sql_prompt
)

report_generator = LLMChain(
    llm=ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.3, max_tokens=2048), 
    prompt=generate_report_prompt
)

report_enhancer = LLMChain(
    llm=ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.5, max_tokens=2048), 
    prompt=enhance_analysis_prompt
)

def perform_analysis(objective, table_name, path_to_db, schema, n_queries, verbose=False):
    
    # generate questions
    if verbose:
        print(f'{color.BOLD}Objective{color.END}: {objective}')
        print('🤔 Generating questions')

    questions = question_generator.run({
        'objective': objective, 
        'table_name': table_name,
        'schema': schema,
        'n_queries': n_queries
    })
    questions = extract_questions(questions)

    # generate sql queries
    if verbose:
        print('🧑‍💻 Generating queries to answer each question')

    iterator_maybe_tqdm = tqdm(questions) if verbose else questions
    queries = [query_generator.run({'question': q, 'table_name': table_name, 'schema': schema}) for q in iterator_maybe_tqdm]
    queries_only_list = [extract_first_sql_query(q) for q in queries]

    # execute queries
    if verbose:
        print(f'📊 Executing queries against table "{table_name}"...', end='')
    answers = [query_database(path_to_db, q, max_rows=10) for q in queries_only_list]
    total_completed = len([a for a in answers if str(a) != QUERY_FAILED])
    if verbose:
        print(f'{total_completed}/{len(answers)} queries succeeded.')
    
    # generate report
    if verbose:
        print(f'📝 Generating report')
    data_for_report = [{'question': q, 'answer': a} for q, a in zip(questions, answers)]
    data_for_report = [x for x in data_for_report if str(x['answer']) != QUERY_FAILED]
    
    
    report = report_generator.run({'data': data_for_report, 'objective': objective})
    
    # enhance report
    if verbose:
        print(f'✨ Enhancing report')
    enhanced_report = report_enhancer.run(report)

    return enhanced_report

if __name__ == '__main__':

    objective = 'We want to identify potential cases of employees being overpaid'
    table_name = 'salaries_sampled'
    path_to_db = Path.cwd() / 'nyc_salaries_sampled.db'
    schema = get_schema(path_to_db, table_name)
    n_queries = 7

    full_report = perform_analysis(
        objective=objective,
        table_name=table_name,
        path_to_db=path_to_db,
        schema=schema,
        n_queries=n_queries,
        verbose=True
    )
    print()
    print(full_report)