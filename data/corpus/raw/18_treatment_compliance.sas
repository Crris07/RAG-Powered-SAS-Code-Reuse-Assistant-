/* ADaM Utility - Treatment Compliance */
/* Calculates exposure compliance from planned versus actual dose */

data compliance;
  merge adam.adex(in=a) adam.adsl(keep=usubjid trtp saffl);
  by usubjid;
  if a;

  planned_dose = 100;
  planned_days = 28;
  expected_cumdose = planned_dose * planned_days;
  compliance_pct = 100 * cumdose / expected_cumdose;

  length complfl $1;
  complfl = ifc(compliance_pct >= 80, 'Y', 'N');
run;

proc means data=compliance n mean std median min max;
  class trtp;
  var compliance_pct;
  output out=compliance_summary n=n mean=mean std=std median=median min=min max=max;
run;
