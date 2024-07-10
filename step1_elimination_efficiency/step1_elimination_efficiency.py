import pandas as pd
from openai import AzureOpenAI
import json
import openai
import sys
import os
import pickle

sys.path.append(os.path.join(os.getcwd(), '..'))

from prompts import *

employment_ground_truth = pd.read_csv('../eval_employment_prompt.csv')
relation_ground_truth = pd.read_csv('../eval_relationship_prompt.csv')

relation_df = relation_ground_truth[['RELATIONSHIP_nonadverse', 'RELATIONSHIP_adverse']]

final_df = employment_ground_truth.join(relation_df, on='index', how='left')

with open('../azure_credentials.json', 'r') as file:
    azure_data = json.load(file)
    api_key = azure_data['API_KEY']
    api_version = azure_data['API_VERSION']
    azure_endpoint = azure_data['AZURE_ENDPOINT']
    azure_deployment_name = azure_data['AZURE_DEPLOYMENT_NAME']

client = AzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint = azure_endpoint
    )

deployment_name=azure_deployment_name #This will correspond to the custom name you chose for your deployment when you deployed a model. Use a gpt-35-turbo-instruct deployment.

# Defining a function to create the prompt from the instruction system message, the few-shot examples, and the current query
def create_prompt(system_message, user_message):    
    formatted_message = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]
    
    return formatted_message

# This function sends the prompt to the GPT model
def send_message(message, model_name, max_response_tokens=500):
    response = client.chat.completions.create(
        model=model_name,
        messages=message,
        temperature=0,
        max_tokens=max_response_tokens,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    
    return response.choices[0].message.content.strip()

# 500-1000
index_list = []
llm_response_list = []
system_message = "You are an information extract tool that follows instructions very well and is specifically trained to extract social determinants of health elements from hospital generated free-text."

try:
    for index, row in final_df[3916:4000].iterrows():
        free_text = row['text']
        user_message = step1_query_optimized.format(free_text=free_text)
        openai_message = create_prompt(system_message, user_message)
        response = send_message(openai_message, deployment_name)
        
        index_list.append(index)
        llm_response_list.append(response)
        print(index)
        print(free_text)
        print(response)
        print()
except Exception as err:
    print("Something went wrong: ", err)
    
llm_3916_4000_step1 = pd.DataFrame({'index': index_list, 'llm_3916_4000_step1': llm_response_list})

with open('llm_3916_4000_step1.pkl', 'wb') as file:
    pickle.dump(llm_3916_4000_step1, file)
