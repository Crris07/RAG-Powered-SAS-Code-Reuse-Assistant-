/* Listing - Medical History */
/* Summarizes relevant baseline medical history */

data mh_listing;
  merge sdtm.mh(in=a) adam.adsl(keep=usubjid trtp saffl);
  by usubjid;
  if a;

  length activefl $1;
  activefl = ifc(mhongo = 'Y', 'Y', 'N');
  keep usubjid trtp saffl mhterm mhdecod mhcat mhstdtc mhendtc activefl;
run;

proc sort data=mh_listing;
  by trtp usubjid mhcat mhdecod;
run;

proc report data=mh_listing nowd;
  columns trtp usubjid mhcat mhterm mhstdtc mhendtc activefl;
  title 'Medical History Listing';
run;
