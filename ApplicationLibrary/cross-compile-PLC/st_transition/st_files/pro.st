PROGRAM program0
  VAR
    MG90S AT %QW0 : UINT := 0;
  END_VAR
  VAR
    start_quare : BOOL := 1;
    tmp_start : BOOL := 0;
    TON0 : TON;
    TON1 : TON;
    _TMP_SEL28_OUT : UINT;
  END_VAR

  TON0(IN := NOT(tmp_start), PT := T#2s);
  start_quare := TON0.Q;
  TON1(IN := start_quare, PT := T#2s);
  tmp_start := TON1.Q;
  _TMP_SEL28_OUT := SEL(start_quare, 0, 180);
  MG90S := _TMP_SEL28_OUT;
END_PROGRAM


CONFIGURATION Config0

  RESOURCE Res0 ON PLC
    TASK task0(INTERVAL := T#0.1ms,PRIORITY := 0);
    PROGRAM instance0 WITH task0 : program0;
  END_RESOURCE
END_CONFIGURATION
