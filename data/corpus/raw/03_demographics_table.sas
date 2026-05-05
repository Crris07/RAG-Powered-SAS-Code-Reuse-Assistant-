/* Demographics and Baseline Characteristics Summary Table */
/* Produces Table 14.1 demographics summary by treatment */

proc means data=adam.adsl n mean std min max;
  class trtp;
  var age height weight;
  output out=demo_stats;
run;

/* Demographics summary table */
data demo_summary;
  set adam.adsl;
  by trtp;
  
  if first.trtp then do;
    n_subj = 0;
    sum_age = 0;
    sum_male = 0;
  end;
  
  n_subj + 1;
  sum_age + age;
  sum_male + male;
  
  if last.trtp then do;
    mean_age = sum_age / n_subj;
    pct_male = sum_male / n_subj * 100;
  end;
run;

/* Format for output */
proc format;
  value pctfmt 0-<50 = '[0-50)'
               50-<75 = '[50-75)'
               75-100 = '[75-100]';
run;

/* Final summary table */
proc tabulate data=demo_summary;
  class trtp;
  var n_subj mean_age pct_male;
  
  table trtp,
        n_subj=' '
        mean_age=' '
        pct_male=' ';
  
  title 'Table 1. Demographics and Baseline Characteristics';
run;
