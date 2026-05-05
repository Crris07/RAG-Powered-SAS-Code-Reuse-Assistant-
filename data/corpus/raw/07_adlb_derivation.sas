/* ADLB Derivation - Analysis Laboratory Data */
/* Derives baseline, change from baseline, and abnormality flags */

proc sort data=sdtm.lb out=lb_sorted;
  by usubjid paramcd lbdtc;
run;

data adlb_pre;
  merge lb_sorted(in=a) adam.adsl(keep=usubjid trtsdt trtp saffl);
  by usubjid;
  if a;

  format adt date9.;
  adt = input(lbdtc, yymmdd10.);
  aval = input(lborres, best.);
  avisit = visit;
run;

proc sql;
  create table lb_base as
  select usubjid, paramcd, aval as base
  from adlb_pre
  where adt <= trtsdt
  group by usubjid, paramcd
  having adt = max(adt);
quit;

data adlb;
  merge adlb_pre lb_base;
  by usubjid paramcd;

  chg = aval - base;
  if base > 0 then pchg = 100 * chg / base;

  length anl01fl highfl lowfl $1;
  anl01fl = 'Y';
  highfl = ifc(aval > lbstresn * 1.2, 'Y', 'N');
  lowfl = ifc(aval < lbstresn * 0.8, 'Y', 'N');

  keep usubjid trtp saffl paramcd param aval base chg pchg avisit adt anl01fl highfl lowfl;
run;
