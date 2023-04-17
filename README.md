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
