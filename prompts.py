from langchain.prompts import PromptTemplate

generate_questions_prompt = PromptTemplate(
    input_variables=['objective', 'table_name', 'schema', 'n_queries'],
    template='''
# Context
Your job is to generate useful insights from large datasets. 

# Task
The overall objective is {objective}. Generate {n_queries} interesting questions that can be answered with the table mentioned below. 

# Table schema
Table name: {table_name}
Table columns and data types: {schema}

# Questions
'''
)

generate_sql_prompt = PromptTemplate(
    input_variables=['question', 'schema', 'table_name'],
    template='''
# Context
Your job is to write a sql query that answers the following question:
{question}

Below is a list of columns and their datatypes. Your query should only use the data contained in the table. The table name is `{table_name}`.

# Columns and datatypes
{schema}

If the question is not a question or is answerable with the given columns, respond to the best of your ability.
Do not use columns that aren't in the table.
Ensure that the query runs and returns the correct output.

# Query:
'''
)

rearrange_prompt = PromptTemplate(
    input_variables=['facts'],
    template='''
# Context
Your job is to rearrange a list of facts into a narrative. 
The rearranged list should have the same facts, but in an order that makes the narrative stronger.
You don't have to use every fact

# Task
Rearrange the following list of facts to make the narrative stronger. It's ok to omit facts that don't fit neatly into the overall narrative.
Be sure to start the response with a list of the ordered facts. Then include a short summary of the narrative.

##### EXAMPLE ######
Facts:
1. Joe missed the bus this morning
2. Joe woke up late
3. Turtles are green
4. Joe doesn't think he did well on his exam

New order and narrative:
[2, 1, 4] Joe got off to a bad start that day. Not only did he wake up late, he missed the bus. This likely caused him to perform poorly on his exam.
####################

# Facts:
{facts}

# New order and narrative::
'''
)


generate_report_prompt = PromptTemplate(
    input_variables=['data', 'objective', 'narrative'],
    template='''
# Context
Your job is to present data using narrative and data storytelling. Below is a set of questions, answers, and methods.
Present this data as a full data analysis. You should aim to aggregate it all into a cohesive narrative that effectively presents the findings.
Don't rearrange the datapoints, as they've already been arranged.
The response should have a few major points that come together to paint a larger picture.

# Here's the overall task
{objective}

# Here's the narrative we're aiming to communicate:
{narrative}

# Here's the data
{data}

# Your analysis
'''
)

generate_methodology_prompt = PromptTemplate(
    input_variables=['question', 'query'],
    template='''
# Context
Your job is to explain the methodology behind a sql query. The answer should be very short, 2 sentences max

# Example
Question: Who sold the most widgets?
Query: SELECT employee_name FROM employee_sales ORDER BY widgets_sold DESC LIMIT 1
Methodology: We sort the sales tables by widgets sold and return the employee with the most sales

# Question
{question}

# Query
{query}

# Methodology
'''
)


enhance_analysis_prompt = PromptTemplate(
    input_variables=['report'],
    template='''
# Context
Your job is to make basic data reports more engaging. Rewrite the analysis below to make it more engaging and compelling.
Add context to the beginning if necessary, feel free to embellish or tell an interesting anecdote. Focus on weaving the findings into a strong, compelling narrative.

# Raw analysis
{report}

# Enhanced analysis
'''
)

summarizer_prompt = PromptTemplate(
    input_variables=['report'],
    template='''
# Context
Your job is to condense and simplify reports for you company's CEO. Condense the following report into a short, 5 bullet point summary.

# Raw analysis
{report}

# Summary
'''
)