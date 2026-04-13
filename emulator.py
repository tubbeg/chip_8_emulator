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
    def clear(self): return
    def draw(self, opcode): return

class Emulator():
    def __init__(self) -> None:
        self.memory = None
        self.screen = Screen()
        self.registers = {
            "vr":bytearray(16),
            "i":0, # index and program counter are represented with ints
            "pc":0x200 # should actually be 12bit and 16bit
        }
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
    def set_pc(self, opcode):
        address = 0x0FFF & opcode
        self.registers["pc"] = address
    def get_register_x(self, opcode):
        h,_ = opcode
        return h & 0x0F
    def get_nn(self, opcode):
        _,l = opcode
        return l.to_bytes()
    def get_nnn(self,opcode):
        h,l = opcode
        return bytes_to_word(h,l)
    def v_add(self, opcode):
        vreg = self.get_register_x(opcode)
        add_nn = self.get_nn(opcode)
        self.registers["vr"][vreg] += add_nn
    def set_vreg(self,opcode):
        vreg = self.get_register_x(opcode)
        set_nn = self.get_nn(opcode)
        self.registers["vr"][vreg] = set_nn
    def set_i(self,opcode):
        set_nnn = self.get_nnn(opcode)
        self.registers["i"] = set_nnn
    def execute_instruction(self,result):
        if result:
            instruction, opcode = result
            match instruction:
                case Instruction.CLEAR: return self.screen.clear()
                case Instruction.JMP: return self.set_pc(opcode)
                case Instruction.SET: return self.set_vreg(opcode)
                case Instruction.ADD: return self.v_add(opcode)
                case Instruction.SETI: return self.set_i(opcode)
                case Instruction.DRAW: return self.screen.draw(opcode)
                case _: return
        return
    def terminate(self):
        while self.run_program:
            if input("Abort? (Y)") == "Y":
                self.run_program = False
    def run_cpu_loop(self):
        if self.memory:
            t = threading.Thread(target=self.terminate)
            t.start()
            while self.run_program:
                instruction = self.get_instruction() # decode opcode/fetch instruction
                self.registers["pc"] = self.registers["pc"] + 2 # increment pc by two (each instruction is 16-bit)
                self.execute_instruction(instruction) # execute instruction
            t.join()


if __name__ == "__main__":
    print("hellooo")
    a = Instruction.CLEAR
    path = "test.ch8"
    e = Emulator()
    e.read_rom(path)
    e.load_rom_to_memory()
    e.run_cpu_loop()


