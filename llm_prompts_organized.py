##### EMPLOYMENT attributes #####
def llm_to_json(free_text, print_prompt=False):
  
  query = f"""
  This prompt consists of two sections: "Instruction" and "Input" which contains a clinical free-text from electronic healht records for you to parse.
  
  Section 1: Instruction
  From the double bracketed <<text>> at the end, for each of the following categories, determine the attribute that accurately describes the status of the patient at the time of <<text>>. The category is shown in double quote and the attributes are shown in square brackets: 

  "EMPLOYMENT": ['“EMPLOYMENT_adverse”', '“EMPLOYMENT_nonadverse”', 'UNKNOWN'];

  You must create key-value pair in json formats:   
  <category>: <estimated attribute from the list of allowed values>,   
  <category>_CD: <the certainty degree of your estimation: [0.00, 1.00]>,    
  <category>_evidence: < brief evidence from <<text>> supporting the attribute you choose >. 

  The EMPLOYMENT attributes are: “EMPLOYMENT_adverse”; “EMPLOYMENT_nonadverse”; UNKNOWN.
  The category UNKNOWN means the <<text>> does not mention information regarding the current employment status of the patient at the time of <<text>>.
  The category “EMPLOYMENT_adverse” may only be assigned if <<text>> explicitly mentions an adverse type of employment status including currently unemployed, underemployed, or has disability. Do not infer this category.
  The category “EMPLOYMENT_nonadverse” may only be assigned if <<text>> explicitly mentions a non-adverse type of employment status including currently employed, currently a student, or currently retired.
  Do not infer the impact of <<text>> onto the attributes, focus on the factual information only. 
  Even if the patient expresses concerns over a change in their employment status, at the time of <<text>> the patient is still considered to maintain their original status. For example "fear that she will lose her current job" is considered “EMPLOYMENT_nonadverse”.
  Focus on the status of the patient only, and NOT the status of their family members.
  Being a student is considered “EMPLOYMENT_nonadverse” in this context.
  
  Section 2: Input
  <<{free_text}>>
  """

  if print_prompt:
     print('Prompted used: \n', query)

  message_text = [
    {"role":"system","content":"You are an information extract tool that follows instructions very well and is specifically trained to extract social determinants of health elements from hospital generated free-text."},
    {'role': 'user', 'content': query},
    ]

  response = openai.ChatCompletion.create(
    engine=DEPLOYMENT_NAME,
    messages = message_text,
    temperature=0,
    max_tokens=1500,
    top_p=0.95,
    frequency_penalty=0,
    presence_penalty=0,
    stop=None,
    response_format={ "type": "json_object" }
  )
  raw_response = response['choices'][0]['message']['content']
  # json_response = json.loads(raw_response)
  # print(json_response)

  return raw_response

##### RELATIONSHIP attributes #####
query = f"""
This prompt consists of two sections: "Instruction" and "Input" which contains a clinical free-text from electronic healht records for you to parse.
  
  Section 1: Instruction
  From the double bracketed <<text>> at the end, for each of the following categories, determine the attribute that accurately describes the status of the patient at the time of <<text>>. The category is shown in double quote and the attributes are shown in square brackets: 

  "marital_status": ['married', 'divorced', 'widowed', 'partnered', 'single', 'UNKNOWN'];

  You must create key-value pair in json formats:   
  <category>: <estimated attribute from the list of allowed values>,   
  <category>_CD: <the certainty degree of your estimation: [0.00, 1.00]>,    
  <category>_evidence: < brief evidence from <<text>> supporting the attribute you choose >. 

  The attribute UNKNOWN means the <<text>> does not mention information regarding the current martial status of the patient at the time of <<text>>.
  If there is explicit mentioning of husband, wife, girlfriend, boyfriend, or single, you MUST not classify the relationship as UNKNOWN. 
  If there is no evidence of a current or previous romantic partner or spouse mentioned in the text, you MUST classify the martial status as UNKNOWN.
  The mentioning of girlfriend or boyfriend is considered evidence of a current romantic partner.
  Focus on the patient's romantic relationship only, do NOT consider family member's romantic relationship. For example, "the patient's parents' divorce" does NOT contain sufficient evidence for the patient's current martial status.

  Do not infer the impact of <<text>> onto the attributes, focus on the factual information only. 
  Do not consider the emotional relationship of between the patient and family members, focus on the factual martial status only. For example, "having an abusive partner" is still considered "partnered" because the patient currently has a partner.
  Do not consider any relationship between the patient and non-romantic partners.

  Section 2: Input
  <<{free_text}>>
"""