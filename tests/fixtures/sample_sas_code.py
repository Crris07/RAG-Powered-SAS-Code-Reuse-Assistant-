"""Test fixtures - Sample SAS code"""

SAMPLE_SAS_CODE = """
/* Sample SAS Data Step */
data work.mydata;
  set input.raw_data;
  
  /* Derive new variables */
  age_group = put(age, agegroup.);
  
  /* Apply inclusion/exclusion criteria */
  if age >= 18 and age <= 75 then include_flag = 1;
  else include_flag = 0;
  
  keep subjid age include_flag;
run;
"""

SAMPLE_REQUIREMENT_1 = "Generate ADSL (subject-level analysis dataset) with safety flags"
SAMPLE_REQUIREMENT_2 = "Create listing of adverse events for regulatory submission"
SAMPLE_REQUIREMENT_3 = "Calculate demographics summary by treatment group"
