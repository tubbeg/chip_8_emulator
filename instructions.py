from enum import Enum

class Instruction(str,Enum):
    CALL="CALL",        #0nnn
    CLEAR="CLEAR",      #00e0 
    RET="RET",          #00ee
    JMP="JMP",          #1nnn 
    SBR="SBR",          #2nnn
    IF="IF",            #3xnn
    IFNOT="IFNOT",      #4xnn
    IFV="IFV",          #5xy0
    SET="SET",          #6xyn 
    ADD="ADD",          #7xyn
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
    SETI="SETI",        #annn 
    # Note! In AVR, JMP and RJMP refers to how many bytes the instruction is, and not
    # if it adds any register value. I just really like the name RJMP
    RJMP="RJMP",        #bnnn
    RAND="RAND",        #cxnn
    DRAW="DRAW",        #dxyn
    IFKEY="IFKEY",      #ex9e
    IFNKEY="IFNKEY",    #exa1
    GDELAY="GDELAY",    #fx07
    GKEY="GKEY",        #fx0a
    SDELAY="SDELAY"     #fx15
    SOUND="SOUND",      #fx18
    ADDI="ADDI",        #fx1e
    SETIV="SETIV"       #FX29
    BCD="BCD",          #fx33
    STORE="STORE",      #fx55
    RELOAD="RELOAD",    #FX65


    