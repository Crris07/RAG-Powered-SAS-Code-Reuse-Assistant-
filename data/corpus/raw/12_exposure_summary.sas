/* ADEX Summary - Treatment Exposure */
/* Derives duration and cumulative dose */

proc sort data=sdtm.ex out=ex_sorted;
  by usubjid exstdtc;
run;

data adex;
  merge ex_sorted(in=a) adam.adsl(keep=usubjid trtp saffl);
  by usubjid;
  if a;

  format astdt aendt date9.;
  astdt = input(exstdtc, yymmdd10.);
  aendt = input(exendtc, yymmdd10.);
  exdur = aendt - astdt + 1;
  dose = exdose;
  cumdose = dose * exdur;

  keep usubjid trtp saffl astdt aendt exdur dose cumdose extrt;
run;

proc means data=adex n mean std median min max;
  class trtp;
  var exdur cumdose;
  output out=exposure_summary n=n mean=mean std=std median=median min=min max=max;
run;
