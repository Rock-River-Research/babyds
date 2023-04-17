# 🍼🔬 BabyDS
An AI-powered data science pipeline

<img src="https://github.com/Rock-River-Research/babyds/blob/main/babyds.png" width="200px" style="display: block; margin: 0 auto">

-------

BabyDS is an LLM-powered data pipeline that performs data analysis towards a given objective. It's currently in its V0 stage, and there's more work to be done. Namely:
- Performing the query writing step in parallel
- Doing some sort of fact selection and ordering after the data analysis to sharpen the narrative
- Allowing the AI to suggest and answer new questions.

# How to run it
The program is fairly straight-forward. Navigate to the base directory and run `python3 babyds`. In order to change the data source or the objective, change the arguments to the `perform_analysis()` function. Ensure that you have an OpenAI key (`OPENAI_API_KEY`) set in your environment. Get one [here](https://platform.openai.com/account/api-keys) 

# Example Outputs
All examples are from a sampled [NYC Public Servant Salaries dataset](https://data.cityofnewyork.us/widgets/k397-673e?mobile_redirect=true) with the objective: "We want to identify potential cases of employees being overpaid"

> Let's start with the good news: the average base salary for public employees in New York City has been on the rise. In 2018, the average base salary was $45,508.538, and by 2022, it had increased to $48,426.018. That's a modest increase, but it's still a positive trend.
>
> But when we look at the total other pay received by public employees, the numbers are truly staggering. In just ten fiscal years, the total other pay received by public employees in New York City has more than doubled. In 2014, the total other pay received was $1,149,076,637.61, and by 2022, it had increased to $2,740,086,013.70. That's a substantial increase, and it raises some important questions about how and why public employees are receiving so much more in other pay.

> Furthermore, we discovered that almost 50,000 employees received a salary increase of more than 10% from the previous fiscal year. While some of these increases may be justified due to exceptional performance, it's difficult to ignore the possibility of favoritism or nepotism at play. This raises concerns about whether the salary increases were truly based on merit or if they were merely a result of personal connections.

> Firstly, the agency with the highest average salary is the Board of Correction, with an average salary of $87,251. This may come as a surprise to some, as many assume that high-paying agencies are reserved for executives and top-level management. On the other end of the spectrum, the Board of Elections Poll Workers has an average salary of only $1. This could be due to the fact that poll workers are typically temporary hires who work on election days only.
