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