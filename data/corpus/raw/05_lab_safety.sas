/* Safety Analysis - Laboratory Values */
/* Identification of potentially clinically significant abnormalities */

data lab_safety;
  set adam.adlb;
  
  /* Flag potentially clinically significant (PCS) abnormalities */
  pcs_flag = 0;
  
  if paramcd = 'ALB' then do;
    if aval < 3.0 or aval > 4.5 then pcs_flag = 1;
  end;
  
  if paramcd = 'AST' then do;
    if aval > 80 then pcs_flag = 1;
  end;
  
  if paramcd = 'ALT' then do;
    if aval > 80 then pcs_flag = 1;
  end;
  
  if paramcd = 'CREAT' then do;
    if aval > 1.5 then pcs_flag = 1;
  end;
  
  keep subjid paramcd aval visitnum pcs_flag trtp;
run;

/* Summary of PCS findings */
proc freq data=lab_safety;
  table paramcd * pcs_flag / out=pcs_summary;
  where pcs_flag = 1;
run;

/* Detailed report */
proc report data=lab_safety nowd
  columns subjid paramcd aval pcs_flag trtp;
  define subjid / display 'Subject ID';
  define paramcd / display 'Lab Parameter';
  define aval / display 'Value';
  define pcs_flag / display 'PCS Flag';
  define trtp / display 'Treatment';
  
  where pcs_flag = 1;
  
  title 'Potentially Clinically Significant Laboratory Abnormalities';
run;

/* Statistical summary */
proc means data=lab_safety n mean std min max;
  class paramcd trtp;
  var aval;
  
  title 'Laboratory Values Summary Statistics';
run;
