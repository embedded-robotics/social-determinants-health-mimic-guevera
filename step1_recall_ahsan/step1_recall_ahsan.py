import pandas as pd
import openai
import os
import pickle
from openai import AzureOpenAI
import sys
import json
import time

sys.path.append(os.path.join(os.getcwd(), '..'))

from prompts import *

UNIQUE_ID_COLUMN_NAME = "ROW_ID"
UNIQUE_TEXT_COLUMN_NAME = "TEXT"
UNIQUE_LABEL_COLUMN_NAMES = ['sdoh_economics','sdoh_environment']
# Economics (0: None, 1: True[Non-Adverse], 2: False[Adverse])
# Environment (0: None, 1: True[Non-Adverse], 2: False[Adverse])

def retrieve_social_history(df):
    replace_texts = []
    for row_id in df[UNIQUE_ID_COLUMN_NAME]:
        patient = df[df[UNIQUE_ID_COLUMN_NAME] == row_id][UNIQUE_TEXT_COLUMN_NAME].iloc[0]
        social_history_start = patient.lower().find('social history:')
        pos_ends = []
        pos_ends.append(patient.lower().find('family history:'))
        pos_ends.append(patient.lower().find('physical exam'))
        pos_ends.append(patient.lower().find('medications:'))
        pos_ends.append(patient.lower().find('hospital course:'))
        pos_ends.append(patient.lower().find('review of systems:'))
        pos_ends = [x for x in pos_ends if x > social_history_start]
        pos_ends.append(social_history_start+500)
        social_history_end = min(pos_ends)
        replace_texts.append((row_id,patient[social_history_start:social_history_end]))
    texts = pd.DataFrame(replace_texts,columns =[UNIQUE_ID_COLUMN_NAME,UNIQUE_TEXT_COLUMN_NAME])
    
    return texts

#Paths to MIMIC_CSVs
MIMIC_ADMISSION_CSV = "../ahsan_data/ADMISSIONS.csv" #Fill in path/to/file with the path to your MIMIC-III folder
MIMIC_NOTEEVENTS_CSV = "../ahsan_data/NOTEEVENTS.csv" #Fill in path/to/file with the path to your MIMIC-III folder
MIMIC_SBDH = "../ahsan_data/MIMIC-SBDH.csv" #Fill in path/to/file with the path to your MIMIC-SBDH folder

df = pd.read_csv(MIMIC_ADMISSION_CSV)
notes_df = pd.read_csv(MIMIC_NOTEEVENTS_CSV)

#Loading DataFrames for Annotated and Unnanotated MIMIC Notes

newborn_list = df[df["ADMISSION_TYPE"] == "NEWBORN"].SUBJECT_ID.to_list()
discharge_df = notes_df[notes_df['CATEGORY'] == 'Discharge summary']
non_neonatal = discharge_df[~discharge_df['SUBJECT_ID'].isin(newborn_list)]

sbdh_data = pd.read_csv(open(MIMIC_SBDH, 'r+', encoding='UTF-8'),encoding='UTF-8', on_bad_lines='warn')
sbdh_data = sbdh_data.rename(columns={'row_id':UNIQUE_ID_COLUMN_NAME})

annotated_list = sbdh_data[UNIQUE_ID_COLUMN_NAME].tolist()
annotated_notes = discharge_df[discharge_df[UNIQUE_ID_COLUMN_NAME].isin(annotated_list)]
annotated_subjects = discharge_df[discharge_df[UNIQUE_ID_COLUMN_NAME].isin(annotated_list)].SUBJECT_ID.to_list()

no_soc_his = []
for index, row in non_neonatal.iterrows():
    if 'social history:' not in row[UNIQUE_TEXT_COLUMN_NAME].lower():
        no_soc_his.append(row[UNIQUE_ID_COLUMN_NAME])

final_sdoh_list = non_neonatal[~non_neonatal[UNIQUE_ID_COLUMN_NAME].isin(no_soc_his)]
unnanotated_notes = final_sdoh_list[~final_sdoh_list[UNIQUE_ID_COLUMN_NAME].isin(annotated_list)]

annotated_sh = retrieve_social_history(annotated_notes)
annotated_sh = pd.merge(annotated_sh,sbdh_data[[UNIQUE_ID_COLUMN_NAME] + UNIQUE_LABEL_COLUMN_NAMES],on=UNIQUE_ID_COLUMN_NAME, how='left')
unannotated_sh = retrieve_social_history(unnanotated_notes)

df = newborn_list = notes_df = discharge_df = non_neonatal = annotated_list = annotated_subjects = no_soc_his = final_sdoh_list = unnanotated = sbdh_data = None


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

# Getting the results and saving it
index_list = []
llm_response_list = []
filtered_df = annotated_sh[~((annotated_sh['sdoh_environment'] == 1) | (annotated_sh['sdoh_environment'] == 2) | (annotated_sh['sdoh_economics'] == 1) | (annotated_sh['sdoh_economics'] == 2))]
filtered_df = filtered_df.reset_index(drop=True)
system_message = "You are an information extract tool that follows instructions very well and is specifically trained to extract social determinants of health elements from hospital generated free-text."

start_index = 0
current_index = start_index
total_records = len(filtered_df)

while True:
    try:
        for index in range(start_index, total_records):
            current_index = index
            row = filtered_df.iloc[current_index, :]
            free_text = row['TEXT']
            user_message = step1_query_ahsan.format(free_text=free_text)
            openai_message = create_prompt(system_message, user_message)
            response = send_message(openai_message, deployment_name)
            
            index_list.append(current_index)
            llm_response_list.append(response)
            print(current_index)
            print(free_text)
            print(response)
            print()

    except Exception as err:
        print("Something went wrong: ", err)
        start_index = current_index
        print("Waiting for 10 seconds before continuing again with index:", start_index)
        time.sleep(10)

    # Break the loop if current_index has completed
    if current_index == (total_records - 1):
        break


llm_no_response_step1 = pd.DataFrame({'index': index_list, 'llm_no_response_step1': llm_response_list})

file_name = 'llm_no_response_step1_' + str(start_index) + '_' + str(total_records) + '.pkl'
with open(file_name, 'wb') as file:
    pickle.dump(llm_no_response_step1, file)