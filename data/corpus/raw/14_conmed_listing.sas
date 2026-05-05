/* Listing - Concomitant Medications */
/* Flags medications ongoing during treatment */

data conmed;
  merge sdtm.cm(in=a) adam.adsl(keep=usubjid trtsdt trtedt trtp saffl);
  by usubjid;
  if a;

  format cmstdt cmendt date9.;
  cmstdt = input(cmstdtc, yymmdd10.);
  cmendt = input(cmendtc, yymmdd10.);

  length ontrtfl $1;
  if cmstdt <= trtedt and (missing(cmendt) or cmendt >= trtsdt) then ontrtfl = 'Y';
  else ontrtfl = 'N';

  keep usubjid trtp saffl cmtrt cmdecod cmstdt cmendt ontrtfl;
run;

proc report data=conmed nowd;
  columns trtp usubjid cmtrt cmdecod cmstdt cmendt ontrtfl;
  title 'Concomitant Medications During Treatment';
run;
