step1_query_optimized = '''
You are given a free-text clinical note (<<text>>) from electronic health records. For each of the following categories, determine the attribute that accurately describes the status of the patient at the time of <<text>>. Do not infer the impact of <<text>> onto the attributes, instead focus on the factual information only which is present at the time of <<text>>.
The category is shown in double quotes and the attributes are shown in square brackets: 

1. "EMPLOYMENT": ['Employed', 'Underemployed', 'Unemployed', 'Disability', 'Retired', 'Student'];
2. "TRANSPORTATION": ['Distance', 'Resource'];
3. "HOUSING": ['Poor', 'Undomiciled'];
4. "MARITAL_STATUS": ['Married', 'Partnered', 'Divorced', 'Widowed', 'Single'];
5. "RELATIONSHIP_CONDITION": ['NonAdverse', 'Adverse'];
6. "EMPLOYMENT_CONDITION": ['NonAdverse', 'Adverse'];

After determining the attribute of each category, you must consolidate this information in a ONE word reply i.e., "YES" if a valid attribute is determined for atleast one category, else "NO".
In your final response, do not provide information about each indivdual category or attribute. You must return only "YES" or "NO" in your final response, and nothing else.

Input: <<{free_text}>>
Result:
'''


step1_query = '''
This prompt consists of two sections: "Instruction" and "Input" which contains a clinical free-text from electronic healht records for you to parse.

Section 1: Instruction
From the double bracketed <<text>> at the end, for each of the following categories, determine the attribute that accurately describes the status of the patient at the time of <<text>>. The category is shown in double quote and the attributes are shown in square brackets: 

1. "EMPLOYMENT": ["Employed", "Underemployed", "Unemployed", "Disability", "Retired", "Student", "UNKNOWN"];
2. "TRANSPORTATION": ["Distance", "Resource", "UNKNOWN"];
3. "HOUSING": ["Poor", "Undomiciled", "UNKNOWN"];
4. "MARITAL_STATUS": ["Married", "Partnered", "Divorced", "Widowed", "Single", "UNKNOWN"];
5. "RELATIONSHIP_CONDITION": ["NonAdverse", "Adverse", "UNKNOWN"];
6. "EMPLOYMENT_CONDITION": ["NonAdverse", "Adverse", "UNKNOWN"];

The "UNKNOWN" attribute of each category means the <<text>> does not mention any information regarding other attributes of the category at the time of <<text>>.
For example "she lost her job" mentiones that “EMPLOYMENT_CONDITION” is "Adverse" and "EMPLOYMENT" is "Unemployed" but it does not mention anything about the category "TRANSPORTATION", hence "TRANSPORTAION" should be "UNKNOWN".

You must create key-value pair in json formats for all the categories:
<category>: <estimated attribute from the list of allowed values>,
<category>_CD: <the certainty degree of your estimation: [0.00, 1.00]>,
<category>_evidence: < brief evidence from <<text>> supporting the attribute you choose >.

Do not infer the impact of <<text>> onto the attributes, focus on the factual information only which is present at the time of <<text>>.
Even if the <<text>> concerns over a change in the status of any category, maintain their original attribute status at the time of <<text>>. For example "fear that she will lose her current job" is considered to be "EMPLOYMENT_CONDITION" with “Nonadverse” attribute.

Section 2: Input
<<{free_text}>>
'''

step2_query_employment_condition = """
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

step2_query_marital_status = """
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
