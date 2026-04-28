clearvars
PYNQ_obj = PYNQ_LIB.PYNQ_ML;
StepMot = PYNQ_LIB.PYNQ_StepMot(PYNQ_obj);
StepMot.startMoving(1,100,300);