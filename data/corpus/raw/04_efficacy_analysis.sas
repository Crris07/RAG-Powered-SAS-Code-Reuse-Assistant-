/* Efficacy Endpoint Analysis - Primary */
/* ADAS-cog11 Change from Baseline at Week 12 */

data efficacy;
  set adam.adeff;
  
  /* Derive change from baseline */
  if paramcd = 'ADAS11' then do;
    if avisit = 'BASELINE' then baseline_value = aval;
    if avisit = 'WEEK 12' then do;
      change = aval - baseline_value;
      pct_change = (change / baseline_value) * 100;
    end;
  end;
  
  keep subjid paramcd avisit aval baseline_value change pct_change trtp;
run;

/* Sort data */
proc sort data=efficacy;
  by trtp avisit;
run;

/* Descriptive statistics */
proc means data=efficacy mean std stderr;
  class trtp avisit;
  var aval change pct_change;
  output out=eff_summary;
run;

/* ANCOVA model for primary analysis */
proc glm data=efficacy;
  class trtp;
  model change = trtp baseline_value;
  lsmeans trtp / pdiff;
  output out=glm_output p=pred r=resid;
  
  title 'Primary Efficacy Analysis - ADAS-cog11 Change';
run;

/* T-test comparison */
proc ttest data=efficacy;
  class trtp;
  var change;
  
  title 'Comparison of Change Scores Between Treatment Groups';
run;
