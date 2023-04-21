import re
import sqlite3
from pathlib import Path
import pandas as pd
from tqdm import tqdm
import ast
from numpy import argsort

from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain

from prompts import *

pd.options.display.float_format = '{:.2f}'.format

QUERY_FAILED = '<query_failed>'

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

def query_database(db_path, query, max_rows=15):
    
    try:
        with sqlite3.connect(db_path) as connection:

            cursor = connection.cursor()
            cursor.execute(query)

            rows = cursor.fetchmany(max_rows)   # limit rows
            columns = tuple([x[0] for x in cursor.description])
            
            return pd.DataFrame(rows, columns=columns)
    
    except:
        return '<query_failed>'


def get_schema(db_path, table_name):
    
    command = f"PRAGMA table_info('{table_name}')"
    
    with sqlite3.connect(db_path) as connection:
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

def parse_narrative_arrangement(input_string):
    
    # Find the index of the closing bracket
    closing_bracket = input_string.index("]")

    # Split the string at the first space after the closing bracket
    list_str = input_string[:closing_bracket + 1]
    text = input_string[closing_bracket + 2:]

    # Convert the list string into a list of strings
    list_obj = ast.literal_eval(list_str)

    return list_obj, text


question_generator = LLMChain(
    llm=ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.4, max_tokens=2048), 
    prompt=generate_questions_prompt
)

query_generator = LLMChain(
    llm=ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.1, max_tokens=2048), 
    prompt=generate_sql_prompt
)

methodology_generator = LLMChain(
    llm=ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.0, max_tokens=2048), 
    prompt=generate_methodology_prompt
)

facts_to_narrative = LLMChain(   # a higher temperature actually works here for getting all of the points
    llm=ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.6, max_tokens=2048), 
    prompt=rearrange_prompt
)

report_generator = LLMChain(
    llm=ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.3, max_tokens=2048), 
    prompt=generate_report_prompt
)

report_enhancer = LLMChain(
    llm=ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.5, max_tokens=2048), 
    prompt=enhance_analysis_prompt
)

summarizer = LLMChain(
    llm=ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.5, max_tokens=2048), 
    prompt=summarizer_prompt
)

def perform_analysis(objective, table_name, path_to_db, n_queries, verbose=False):
    
    schema = get_schema(path_to_db, table_name)

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
        

    # aggregate the data and rearrange the facts
    if verbose: 
        print(f'🪚 Crafting the narrative')
    data_for_report = [{'question': q, 'answer': a} for q, a in zip(questions, answers)]
    data_for_report = [x for x in data_for_report if str(x['answer']) != QUERY_FAILED]


    summarized_data = summarizer.run(str(data_for_report))
    arranged_narrative = facts_to_narrative.run(summarized_data)
    ordering, narrative = parse_narrative_arrangement(arranged_narrative)
    ordering = argsort(ordering).tolist()

    ordered_datapoints = [data_for_report[index-1] for index in ordering]

    # generate report
    if verbose: 
        print(f'📝 Generating report')
    report = report_generator.run({
        'data': ordered_datapoints, 
        'objective': objective, 
        'narrative': narrative
    })

    # enhance report
    if verbose:
        print(f'✨ Enhancing report')
    enhanced_report = report_enhancer.run(report)

    return enhanced_report

if __name__ == '__main__':

    objective = 'We want to identify potential cases of employees being overpaid'
    table_name = 'salaries_sampled'
    path_to_db = Path.cwd() / 'nyc_salaries_sampled.db'
    n_queries = 5

    full_report = perform_analysis(
        objective=objective,
        table_name=table_name,
        path_to_db=path_to_db,
        n_queries=n_queries,
        verbose=True
    )

    print()
    print(full_report)