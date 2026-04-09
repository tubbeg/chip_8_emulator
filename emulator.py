from enum import Enum


class Instruction(Enum):
    CLEAR=1,    #00e0 
    JMP=2,      #1nnn 
    SET=3,      #6xyn 
    ADD=4,      #7xyn 
    SETI=5,     #annn 
    DRAW=6,     #dxyn

def is_var_instruction(byte, compare): return byte & 0xF000 == compare

def is_jmp(byte): return is_var_instruction(byte,0x1000)

def is_set(byte): return is_var_instruction(byte,0x6000)

def is_add(byte): return is_var_instruction(byte,0x7000)

def is_seti(byte): return is_var_instruction(byte,0xa000)

def is_draw(byte): return is_var_instruction(byte,0xd000)

def is_clear(byte): return byte & 0x00f0 == 0x00e0

# 4096 bytes memory with first 512 bytes reserved
# big endian

class Emulator():
    def __init__(self) -> None:
        self.memory = {}
        self.registers = {"vr":{}, "i":0, "pc":0x200}
    


class Decoder():
    def __init__(self):
        self.file_contents = None
    def read_rom(self, path):
        with open(path, "rb") as f:
            self.file_contents = f.read()
    def decode(self):
        if self.file_contents:
            for i in self.file_contents:
                print("here here: ",i)



if __name__ == "__main__":
    print("hellooo")
    a = Instruction.CLEAR
    path = "test.ch8"
    dec = Decoder()
    dec.read_rom(path)



