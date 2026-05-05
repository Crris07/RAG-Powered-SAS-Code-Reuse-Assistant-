/* TLF Table - Vital Signs Summary */
/* Mean change from baseline by visit and treatment */

data vs_summary_input;
  set adam.advs;
  where paramcd in ('SYSBP', 'DIABP', 'PULSE', 'WEIGHT');
run;

proc means data=vs_summary_input n mean std median min max nway;
  class trtp paramcd avisit;
  var aval chg;
  output out=vs_summary_stats
    n=n
    mean=mean
    std=std
    median=median
    min=min
    max=max;
run;

proc report data=vs_summary_stats nowd;
  columns trtp paramcd avisit n mean std median min max;
  define trtp / group 'Treatment';
  define paramcd / group 'Parameter';
  define avisit / group 'Visit';
  title 'Vital Signs Summary by Visit';
run;
