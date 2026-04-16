from enum import Enum

class Instruction(str,Enum):
    CLEAR="CLEAR",    #00e0 
    JMP="JMP",      #1nnn 
    SET="SET",      #6xyn 
    ADD="ADD",      #7xyn
    SETI="SETI",     #annn 
    DRAW="DRAW",     #dxyn
