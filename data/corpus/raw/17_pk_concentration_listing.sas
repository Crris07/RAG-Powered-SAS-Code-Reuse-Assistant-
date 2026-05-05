/* Listing - PK Concentrations */
/* Lists concentration values and flags BLQ records */

data pk_conc;
  merge sdtm.pc(in=a) adam.adsl(keep=usubjid trtp saffl);
  by usubjid;
  if a;

  format pctptnum 8. pcstresn best12.;
  length blqfl $1;
  if pcstresc = 'BLQ' then blqfl = 'Y';
  else blqfl = 'N';

  keep usubjid trtp saffl pctpt pctptnum pcdtc pctestcd pcstresn pcstresu blqfl;
run;

proc sort data=pk_conc;
  by trtp usubjid pctptnum;
run;

proc report data=pk_conc nowd;
  columns trtp usubjid pctpt pcstresn pcstresu blqfl;
  title 'PK Concentration Listing';
run;
