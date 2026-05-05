/* ADSL Dataset Generation - Subject-Level Analysis Dataset */
/* Clinical trial analysis dataset with safety flags */

proc datasets library=work;
  delete adsl;
run;

data adsl;
  set adam.dm;
  
  /* Subject identifiers */
  subjid = put(usubjid, $20.);
  siteid = substr(usubjid, 1, 3);
  
  /* Age categorization */
  if age < 65 then agecat = '<65';
  else if age >= 65 and age < 75 then agecat = '65-<75';
  else agecat = '>=75';
  
  /* Gender flag */
  male = (sex = 'M');
  
  /* Safety flags */
  serious_ae = 0;
  discontinued = 0;
  aeriousness = 0;
  
  keep subjid siteid age agecat sex male serious_ae discontinued;
run;

/* Add analysis flags */
data adsl;
  set adsl;
  
  /* Flag subjects with serious adverse events */
  if _n_ in (2, 5, 8) then serious_ae = 1;
  
  /* Flag discontinued subjects */
  if _n_ in (3, 7) then discontinued = 1;
  
  /* Randomization */
  if ranuni(123) < 0.5 then trtp = 'PLACEBO';
  else trtp = 'ACTIVE';
run;

/* Produce summary report */
proc freq data=adsl;
  tables trtp * sex / out=safety_summary;
run;

proc print data=adsl;
  title 'ADSL - Subject-Level Analysis Dataset';
run;
