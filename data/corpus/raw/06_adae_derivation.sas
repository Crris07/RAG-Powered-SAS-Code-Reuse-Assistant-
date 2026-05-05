/* ADAE Derivation - Analysis Adverse Events */
/* Builds treatment-emergent flags and severity summaries */

proc sort data=sdtm.ae out=ae_sorted;
  by usubjid aestdtc aeseq;
run;

data adae;
  merge ae_sorted(in=a) adam.adsl(keep=usubjid trtsdt trtedt trtp saffl);
  by usubjid;
  if a;

  length trtemfl seriousfl relfl $1;
  format astdt aendt date9.;

  astdt = input(aestdtc, yymmdd10.);
  aendt = input(aeendtc, yymmdd10.);

  if astdt >= trtsdt then trtemfl = 'Y';
  else trtemfl = 'N';

  seriousfl = ifc(aeser = 'Y', 'Y', 'N');
  relfl = ifc(aerel in ('RELATED', 'PROBABLE', 'POSSIBLE'), 'Y', 'N');

  if aesev = 'MILD' then asevn = 1;
  else if aesev = 'MODERATE' then asevn = 2;
  else if aesev = 'SEVERE' then asevn = 3;

  keep usubjid trtp saffl aeseq aeterm aesoc astdt aendt aesev asevn trtemfl seriousfl relfl;
run;

proc freq data=adae;
  where trtemfl = 'Y';
  tables trtp * aesev / out=adae_severity_summary;
run;
