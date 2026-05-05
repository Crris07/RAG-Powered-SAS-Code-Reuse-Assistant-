/* Listing - Protocol Deviations */
/* Identifies important deviations by category and treatment */

data protocol_deviation;
  merge sdtm.dv(in=a) adam.adsl(keep=usubjid trtp saffl);
  by usubjid;
  if a;

  length majorfl $1;
  if upcase(dvterm) in ('INCLUSION CRITERIA NOT MET', 'PROHIBITED MEDICATION') then majorfl = 'Y';
  else majorfl = 'N';

  keep usubjid trtp saffl dvcat dvterm dvstdtc majorfl;
run;

proc sort data=protocol_deviation;
  by descending majorfl trtp usubjid;
run;

proc report data=protocol_deviation nowd;
  columns trtp usubjid dvcat dvterm dvstdtc majorfl;
  title 'Protocol Deviation Listing';
run;
