from enum import Enum

class Instruction(str,Enum):
    CLEAR="CLEAR",      #00e0 
    JMP="JMP",          #1nnn 
    SET="SET",          #6xyn 
    ADD="ADD",          #7xyn
    SETI="SETI",        #annn 
    DRAW="DRAW",        #dxyn
    IF="IF",            #3xnn
    IFNOT="IFNOT",      #4xnn
    IFV="IFV",          #5xy0
    SETV="SETV",        #8xy0
    OR="OR",            #8xy1
    AND="AND",          #8xy2
    XOR="XOR",          #8xy3
    ADC="ADC",          #8xy4
    SBC="SBC"           #8xy5
    