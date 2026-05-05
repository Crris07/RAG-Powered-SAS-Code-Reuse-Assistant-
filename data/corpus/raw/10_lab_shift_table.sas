/* TLF Table - Laboratory Shift From Baseline */
/* Summarizes normal/low/high shifts by treatment */

data lab_shift;
  set adam.adlb;
  where anl01fl = 'Y' and paramcd in ('ALT', 'AST', 'BILI', 'CREAT');

  length basecat postcat $8;
  if base < lbstnrlo then basecat = 'LOW';
  else if base > lbstnrhi then basecat = 'HIGH';
  else basecat = 'NORMAL';

  if aval < lbstnrlo then postcat = 'LOW';
  else if aval > lbstnrhi then postcat = 'HIGH';
  else postcat = 'NORMAL';
run;

proc freq data=lab_shift noprint;
  tables trtp * paramcd * basecat * postcat / out=lab_shift_counts;
run;

proc report data=lab_shift_counts nowd;
  columns trtp paramcd basecat postcat count percent;
  define trtp / group 'Treatment';
  define paramcd / group 'Lab Parameter';
  define basecat / group 'Baseline Category';
  define postcat / group 'Postbaseline Category';
  define count / analysis 'n';
  define percent / analysis '%';
  title 'Laboratory Shift Table';
run;
