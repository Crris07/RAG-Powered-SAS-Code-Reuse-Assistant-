/* ADVS Derivation - Analysis Vital Signs */
/* Creates vital signs analysis dataset with baseline and change */

proc sort data=sdtm.vs out=vs_sorted;
  by usubjid vstestcd vsdtc;
run;

data advs_pre;
  merge vs_sorted(in=a) adam.adsl(keep=usubjid trtsdt trtp saffl);
  by usubjid;
  if a;

  format adt date9.;
  paramcd = vstestcd;
  param = vstest;
  aval = vsstresn;
  adt = input(vsdtc, yymmdd10.);
run;

proc sql;
  create table vs_base as
  select usubjid, paramcd, aval as base
  from advs_pre
  where adt <= trtsdt
  group by usubjid, paramcd
  having adt = max(adt);
quit;

data advs;
  merge advs_pre vs_base;
  by usubjid paramcd;

  chg = aval - base;
  length highbpfl $1;
  if paramcd = 'SYSBP' and aval >= 140 then highbpfl = 'Y';
  else if paramcd = 'DIABP' and aval >= 90 then highbpfl = 'Y';
  else highbpfl = 'N';

  keep usubjid trtp saffl paramcd param aval base chg adt highbpfl;
run;
