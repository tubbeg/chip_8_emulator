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
    SBC="SBC",          #8xy5
    SHIFTR="SHIFTR",    #8xy6
    SBCREV="SBCREV",    #8xy7
    SHIFTL="SHIFTL",    #8xye
    IFNOTV="IFNOTV",    #9xy0
    # Note! In AVR, JMP and RJMP refers to how many bytes the instruction is, and not
    # if it adds any number from a register. I just really like the name RJMP
    RJMP="RJMP",        #bnnn
    RAND="RAND"         #cxnn
    