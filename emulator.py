from enum import Enum
import threading
import time

class Instruction(Enum):
    CLEAR=1,    #00e0 
    JMP=2,      #1nnn 
    SET=3,      #6xyn 
    ADD=4,      #7xyn
    SETI=5,     #annn 
    DRAW=6,     #dxyn

def is_var_instruction(word, compare): return word & 0xf000 == compare

def is_clear(byte): return byte & 0x00f0 == 0x00e0

def is_jmp(byte): return is_var_instruction(byte,0x1000)

def is_set(byte): return is_var_instruction(byte,0x6000)

def is_add(byte): return is_var_instruction(byte,0x7000)

def is_seti(byte): return is_var_instruction(byte,0xa000)

def is_draw(byte): return is_var_instruction(byte,0xd000)


# 4096 bytes memory with first 512 bytes reserved
# big endian
# 16b v registers, one program counter (16-bit), one memory (index) register 12 bit

def bytes_to_word(high,low):
    h = high << 8
    return h | low

class Word():
    def __init__(self,high,low) -> None:
        self._high = high
        self._low = low

class Memory():
    def __init__(self, ba) -> None:
        self._memory = bytearray(ba)
    def try_get_opcode(self,pc):
        try:
            high = self._memory[pc]
            low = self._memory[pc + 1]
            return (high,low)
        except:
            return None


class Screen():
    def __init__(self) -> None:
        pass

class Emulator():
    def __init__(self) -> None:
        self.memory = None
        self.screen = {pixel : False for pixel in range(0,16)}
        self.registers = {"vr":[0 for i in range(0, 16)], "i":0, "pc":0x200}
        self.file_contents = None
        self.run_program = True
    def read_rom(self, path):
        with open(path, "rb") as f:
            self.file_contents = f.read()
    def load_rom_to_memory(self):
        if self.file_contents:
            self.memory = Memory(self.file_contents)
    def get_instruction(self):
        if self.memory:
            pc = self.registers["pc"]
            if opcode := self.memory.try_get_opcode(pc):
                h,l = opcode
                b = bytes_to_word(h,l)
                if is_clear(b): return Instruction.CLEAR,opcode
                if is_jmp(b): return Instruction.JMP,opcode
                if is_set(b): return Instruction.SET,opcode
                if is_add(b): return Instruction.ADD,opcode
                if is_seti(b): return Instruction.SETI,opcode
                if is_draw(b): return Instruction.DRAW,opcode
        return None
    def clear_screen(self):
        for pixel in self.screen:
            self.screen[pixel] = False
    def set_pc(self, opcode):
        address = 0x0FFF & opcode
        self.registers["pc"] = address
    def execute_instruction(self,result):
        if result:
            instruction, opcode = result
            match instruction:
                case Instruction.CLEAR: return self.clear_screen()
                case Instruction.JMP: return self.set_pc(opcode)
                case _: return
        return
    def terminate(self):
        while self.run_program:
            i = input("Abort? (Y)") 
            if i == "Y":
                self.run_program = False
    def run_cpu_loop(self):
        if self.memory:
            t = threading.Thread(target=self.terminate)
            print("alive?",t.is_alive())
            t.start()
            print("alive?",t.is_alive())
            while self.run_program:
                instruction = self.get_instruction() # decode opcode/fetch instruction
                self.registers["pc"] = self.registers["pc"] + 2 # increment pc by two (each instruction is 16-bit)
                self.execute_instruction(instruction) # execute instruction
            print("alive?",t.is_alive())
            t.join()
            print("alive?",t.is_alive())


if __name__ == "__main__":
    print("hellooo")
    a = Instruction.CLEAR
    path = "test.ch8"
    e = Emulator()
    e.read_rom(path)
    e.load_rom_to_memory()
    e.run_cpu_loop()


