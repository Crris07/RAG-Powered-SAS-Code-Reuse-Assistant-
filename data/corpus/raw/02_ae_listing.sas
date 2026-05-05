/* TLF Listing - All Adverse Events */
/* Generates listing table of adverse events for regulatory submission */

proc sort data=adam.adae;
  by subjid aeseq;
run;

data ae_listing;
  set adam.adae;
  
  /* Format event dates */
  format aestdtc date9.;
  format aeendtc date9.;
  
  /* Severity categorization */
  if aesev = 'MILD' then sev_num = 1;
  else if aesev = 'MODERATE' then sev_num = 2;
  else if aesev = 'SEVERE' then sev_num = 3;
  
  /* Relationship to drug */
  related = (aerel = 'RELATED');
  
  keep subjid aeterm aestdtc aeendtc aesev aerel aesoc related sev_num;
run;

/* Sort by severity and relationship */
proc sort data=ae_listing;
  by sev_num descending related aeterm;
run;

/* Produce listing */
proc report data=ae_listing nowd
  columns subjid aeterm aestdtc aeendtc aesev related;
  define subjid / display 'Subject ID';
  define aeterm / display 'Adverse Event';
  define aestdtc / display 'Start Date';
  define aeendtc / display 'End Date';
  define aesev / display 'Severity';
  define related / display 'Related';
  
  title 'Listing of All Adverse Events';
run;

/* Export to CSV */
proc export data=ae_listing
  outfile="&output_dir/ae_listing.csv"
  dbms=csv replace;
run;
