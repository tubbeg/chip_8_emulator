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
        self._memory = bytearray(0x1000)
        for i in range(0,0xFFF):
            if i < len(ba):
                self._memory[i] = ba[i]
            else:
                self._memory[i] = 0
    def try_get_index_memory(self, index, rows):
        try:
            #width = 8
            result = []
            for j in range(0,rows):
                byte = self._memory[index + j]
                result.append(byte)
            return result
        except:
            return None
    def try_get_opcode_memory(self,pc):
        try:
            high = self._memory[pc]
            print(high)
            low = self._memory[pc + 1]
            print(low)
            return (high,low)
        except:
            print("pc at: ", pc)
            raise Exception()

def init_screen() : return [[False for _ in range(0,64)] for _ in range(0,32)]


def is_bit_set(byte,nth):
    return (byte & (1<<nth)) 

class Screen():
    def __init__(self) -> None:
        self._screen = init_screen()
    def clear(self):
        print("clearing")
        self._screen = init_screen()
    def set_bit(self, x,y):
        self._screen[x][y] = True
    def reset_bit(self, x,y):
        self._screen[x][y] = False
    def toggle_bit(self,x,y):
        self._screen[x][y] = not self._screen[x][y]
    def draw_bit(self, x,y, bit, byte):
        if is_bit_set(byte,bit):
            self.set_bit(x,y)
        else:
            self.reset_bit(x,y)
    def draw_byte(self, x,y, byte):
        for i in range(0,8):
            self.draw_bit(x + i,y, i, byte)
    def draw(self, opcode, index_register, memory):
        h,l = opcode
        x = 0x0F & h
        y = 0xF0 & l
        #width = 8 # always constant width
        height = 0x0F & l
        if mem := memory.try_get_index_memory(index_register, height):
            for row in range(0,len(mem)):
                byte = mem[row]
                self.draw_byte(x,y + row, byte)
        # which bits are supposed to be true or false?
        # it's determined by the memory pointed by the index register


class Emulator():
    def __init__(self) -> None:
        self.memory = None
        self.screen = Screen()
        self.registers = {
            "vr":bytes(16),
            "i":0, # index and program counter are represented with ints
            "pc":0 # should actually be 12bit and 16bit
            #"pc":0x200 # should actually be 12bit and 16bit
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
            if opcode := self.memory.try_get_opcode_memory(pc):
                h,l = opcode
                b = bytes_to_word(h,l)
                print("return byte: ", b)
                if is_clear(b):return Instruction.CLEAR,opcode
                if is_jmp(b): return Instruction.JMP,opcode
                if is_set(b): return Instruction.SET,opcode
                if is_add(b): return Instruction.ADD,opcode
                if is_seti(b): return Instruction.SETI,opcode
                if is_draw(b): return Instruction.DRAW,opcode
        return None      
    def set_pc(self, opcode):
        h,l = opcode
        b = bytes_to_word(h,l)
        address = 0x0FFF & b
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
        add_nn = int.from_bytes(self.get_nn(opcode))
        l = list(self.registers["vr"])
        l[vreg] += add_nn
        self.registers["vr"] = bytes(l)
    def set_vreg(self,opcode):
        vreg = self.get_register_x(opcode)
        set_nn = self.get_nn(opcode)
        vr = self.registers["vr"]
        l = list(vr)
        l[vreg] = int.from_bytes(set_nn)
        nb = bytes(l)
        self.registers["vr"] = nb
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
                case Instruction.DRAW:
                    index = self.registers["i"]
                    print("drawing...")
                    return self.screen.draw(opcode,index,self.memory)
                case _: return
    def terminate(self):
        while self.run_program:
            if input("Abort? (Y)") == "Y":
                self.run_program = False
    def increment_pc(self):
        self.registers["pc"] = self.registers["pc"] + 2 # increment pc by two (each instruction is 16-bit)
        if self.registers["pc"] > 0xFFF:
            self.registers["pc"] = 0
    def run_cpu_loop(self):
        if self.memory:
            t = threading.Thread(target=self.terminate)
            t.start()
            while self.run_program:
                instruction = self.get_instruction() # decode opcode/fetch instruction
                self.increment_pc()
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


