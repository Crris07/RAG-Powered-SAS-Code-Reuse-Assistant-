data work.demographics;
  set adam.dm;
  
  /* Subject-level demographics for analysis */
  
  /* Age categorization */
  if age < 65 then agecat = '<65';
  else if age >= 65 and age < 75 then agecat = '65-<75';
  else agecat = '>=75';
  
  /* Gender */
  if sex = 'M' then gender = 'Male';
  else gender = 'Female';
  
  /* Treatment group */
  if treatment = 'A' then trtp = 'Active';
  else trtp = 'Placebo';
  
  keep subjid age agecat sex gender trtp;
run;

proc sort data=work.demographics;
  by trtp agecat;
run;

proc report data=work.demographics nowd
  columns trtp agecat N='N' age='Mean Age'n;
  define trtp / group 'Treatment';
  define agecat / group 'Age Category';
  define N / computed;
  compute N;
    N + 1;
  endcomp;
  compute age / mean;
  endcomp;
  
  title 'Demographics by Treatment and Age Category';
run;
