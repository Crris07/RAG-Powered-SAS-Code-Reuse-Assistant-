/* ADTTE Derivation - Time-to-Event Endpoint */
/* Derives time to progression or censoring */

proc sort data=adam.adrs out=rs_sorted;
  by usubjid adt;
run;

data progression;
  set rs_sorted;
  by usubjid;
  where avalc in ('PD', 'PROGRESSIVE DISEASE');
  if first.usubjid;
  eventdt = adt;
  cnsr = 0;
run;

data adtte;
  merge adam.adsl(in=a keep=usubjid trtsdt trtp ittfl) progression(keep=usubjid eventdt cnsr);
  by usubjid;
  if a;

  paramcd = 'PFS';
  param = 'Progression-Free Survival';

  if missing(eventdt) then do;
    eventdt = trtsdt + 168;
    cnsr = 1;
  end;

  aval = eventdt - trtsdt + 1;
  avalu = 'DAYS';

  keep usubjid trtp ittfl paramcd param aval avalu cnsr trtsdt eventdt;
run;

proc lifetest data=adtte plots=survival;
  time aval * cnsr(1);
  strata trtp;
run;
