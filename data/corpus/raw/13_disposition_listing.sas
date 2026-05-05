/* Listing - Subject Disposition */
/* Creates disposition listing with completion and discontinuation reasons */

data disposition;
  merge sdtm.ds(in=a) adam.adsl(keep=usubjid trtp saffl);
  by usubjid;
  if a;

  length completefl discfl $1;
  completefl = ifc(upcase(dsterm) = 'COMPLETED', 'Y', 'N');
  discfl = ifc(index(upcase(dscat), 'DISPOSITION') > 0 and completefl = 'N', 'Y', 'N');

  keep usubjid trtp saffl dsstdtc dscat dsterm completefl discfl;
run;

proc sort data=disposition;
  by trtp descending discfl usubjid;
run;

proc report data=disposition nowd;
  columns trtp usubjid dsstdtc dsterm completefl discfl;
  title 'Subject Disposition Listing';
run;
