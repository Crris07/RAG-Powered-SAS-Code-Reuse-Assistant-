/* Pharmacokinetic Analysis - PK Parameters */
/* Analysis of drug concentration and derived PK parameters */

data pk_analysis;
  set adam.adpc;
  
  /* Derive PK concentration categories */
  if pconc < 10 then conc_cat = 'Low';
  else if pconc >= 10 and pconc < 50 then conc_cat = 'Mid';
  else conc_cat = 'High';
  
  /* Time since dose */
  time_since_dose = pcdtim;
  
  /* Create visit-level summary */
  if avisit in ('WEEK 4', 'WEEK 8', 'WEEK 12') then analysis_visit = 1;
  else analysis_visit = 0;
  
  keep subjid pcdtim pconc conc_cat trtp avisit analysis_visit;
run;

/* Sort for processing */
proc sort data=pk_analysis;
  by subjid pcdtim;
run;

/* Calculate PK parameters by subject */
data pk_summary;
  set pk_analysis;
  by subjid;
  
  if first.subjid then do;
    cmax = pconc;
    tmax = pcdtim;
  end;
  
  if pconc > cmax then do;
    cmax = pconc;
    tmax = pcdtim;
  end;
  
  if last.subjid then output;
  
  keep subjid cmax tmax trtp;
run;

/* Summary statistics by treatment */
proc means data=pk_summary mean std;
  class trtp;
  var cmax tmax;
  
  title 'PK Parameter Summary by Treatment Group';
run;

/* Concentration time profile plot data */
proc sql;
  create table conc_profile as
  select subjid, pcdtim, pconc, conc_cat, trtp
  from pk_analysis
  where analysis_visit = 1
  order by trtp, pcdtim, pconc;
quit;

/* Export for plotting */
proc export data=conc_profile
  outfile="&output_dir/pk_profile.csv"
  dbms=csv replace;
run;
