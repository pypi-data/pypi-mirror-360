let
  a = 10;
  b = 20;
  flag = false;
in
  if
    # numeric comparisons
    (a < b) && !(a == 0) 
  then
    "all checks passed"
  else
    "some check failed"

