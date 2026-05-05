/* TLF Table - Best Overall Response */
/* Summarizes response categories by treatment */

data response;
  set adam.adrs;
  where paramcd = 'BOR' and anl01fl = 'Y';

  length responder $1;
  if avalc in ('CR', 'PR') then responder = 'Y';
  else responder = 'N';
run;

proc freq data=response noprint;
  tables trtp * avalc / out=bor_counts;
  tables trtp * responder / out=response_rate;
run;

proc report data=bor_counts nowd;
  columns trtp avalc count percent;
  define trtp / group 'Treatment';
  define avalc / group 'Best Overall Response';
  define count / analysis 'n';
  define percent / analysis '%';
  title 'Best Overall Response by Treatment';
run;
