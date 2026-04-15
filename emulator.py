from enum import Enum
import threading
import json
import time
import csv
import pygame


class Instruction(str,Enum):
    CLEAR="CLEAR",    #00e0 
    JMP="JMP",      #1nnn 
    SET="SET",      #6xyn 
    ADD="ADD",      #7xyn
    SETI="SETI",     #annn 
    DRAW="DRAW",     #dxyn

class Ch8Byte():
    def __init__(self,nr) -> None:
        self._byte = nr & 0x00FF

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

class Memory():
    def __init__(self, ba) -> None:
        self._memory = bytearray(0x1000)
        for i in range(0,0x1000):
            if i >= 0x200 and i < len(ba) + 0x200:
                self._memory[i] = ba[i - 0x200]
            else:
                self._memory[i] = 0
    def try_get_index_memory(self, index, rows):
            try:
                return self._memory[index:index + rows]
            except:
                return None
    def try_get_opcode_memory(self,pc):
        try:
            high = self._memory[pc]
            low = self._memory[pc + 1]
            return (high,low)
        except:
            print("pc at: ", pc)
            raise Exception()

screen_max_x = 64
screen_max_y = 32
def init_screen() : return [[True for _ in range(0,screen_max_x)] for _ in range(0,screen_max_y)]
def reset_screen() : return [[False for _ in range(0,screen_max_x)] for _ in range(0,screen_max_y)]

def is_bit_set(byte,nth):
    return (byte & (1<<nth)) > 0

class Screen():
    def __init__(self) -> None:
        pass
    def draw_pygame_pixel(self, x, y, w, h, set_bit):
        color = "mintcream"
        if set_bit: color = "blue"
        pygame.draw.rect(self.game_screen, color, (x,y,w,h))
    def update_screen(self):
        self.game_screen.fill("grey")
        x_init,y_init = 50,50
        x,y = x_init,y_init
        for row in self._screen:
            for pixel in row:
                self.draw_pygame_pixel(x,y, 7, 7, pixel)
                x += 10
            x = x_init
            y += 10
        pygame.display.flip()
    def init_screen(self):
        self.game_screen = pygame.display.set_mode((800, 600))
        self._screen = init_screen()
    def clear(self):
        self._screen = reset_screen()
    def set_bit(self, x,y):
        self._screen[y][x] = True
    def reset_bit(self, x,y):
        self._screen[y][x] = False
    def toggle_bit(self,x,y):
        self._screen[y][x] = not self._screen[y][x]
    def draw_bit(self, x,y, byte, nth):
        try:
            if is_bit_set(byte, nth):
                self.set_bit(x,y)
                return False
            s = self._screen[y][x]
            self.reset_bit(x,y)
            if s:
                return True
            return False
        except:
            raise Exception("coord is", x,y)
    def draw_byte(self, x,y, byte):
        #print("drawing byte", byte)
        f = False
        for i in range(0,8):
            #print("drawing bit", i, "is set bit?", is_bit_set(byte, i))
            if self.draw_bit(x + i,y, byte, i):
                f = True
        return f
    def draw(self, opcode, x, y, index_register, memory):
        f = False
        _,l = opcode
        #width = 8 # always constant width
        height = 0x0F & l
        print("COORD IS ", x,y)
        if mem := memory.try_get_index_memory(index_register, height):
            #print("number of rows", height)
            #print("lower byte", l)
            #print(mem, "len:", len(mem))
            j = 0
            for row in mem:
                if self.draw_byte(x,y + j, row):
                    f = True
                j += 1
        return f
    def write_to_disk_csv(self):
        with open("data2.csv", "w") as f:
            w = csv.writer(f)
            w.writerow(self._screen)    
    def write_to_disk_json(self):
        js = json.dumps(self._screen)
        with open("data2.json", "w") as f:
            f.write(js)
        # which bits are supposed to be true or false?
        # it's determined by the memory pointed by the index register


class Emulator():
    def __init__(self) -> None:
        pygame.init()
        self.game_clock = pygame.time.Clock()
        self.memory = None
        self.screen = Screen()
        self.registers = {
            "vr":bytes(16),
            "i":0, # index and program counter are represented with ints
            "pc":0x200 # should actually be 12bit and 16bit
        }
        self.file_contents = None
        self.run_program = True
        self.save_checkpoint = False
        self.instruction_history = []
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
                if is_clear(b):return Instruction.CLEAR,opcode
                if is_jmp(b): return Instruction.JMP,opcode
                if is_set(b): return Instruction.SET,opcode
                if is_add(b): return Instruction.ADD,opcode
                if is_seti(b): return Instruction.SETI,opcode
                if is_draw(b): return Instruction.DRAW,opcode
        print("found none")
        return None      
    def get_nnn(self,opcode):
        h,l = opcode
        b = bytes_to_word(h,l)
        return 0x0FFF & b
    def set_pc(self, opcode):
        #self.registers["pc"] = self.get_nnn(opcode) 
        self.registers["pc"] = self.get_nnn(opcode)
        if self.registers["pc"] > 0xFFF:
            self.registers["pc"] = self.registers["pc"] % 0xFFF
    def get_register_x(self, opcode):
        h,_ = opcode
        return h & 0x0F
    def get_nn(self, opcode):
        _,l = opcode
        #return l.to_bytes()
        return l
    def v_add(self, opcode):
        # does not set carry flag
        vreg = self.get_register_x(opcode)
        #add_nn = int.from_bytes(self.get_nn(opcode))
        add_nn = self.get_nn(opcode)
        l = list(self.registers["vr"])
        #print("ADDING nn", add_nn, "with vreg", l[vreg], "vreg number", vreg)
        l[vreg] += add_nn
        if l[vreg] > 0xFF:
            l[vreg] = l[vreg] % 0xFF
        #print("result", l[vreg])
        self.registers["vr"] = bytes(l)
    def set_vreg(self,opcode):
        vreg = self.get_register_x(opcode)
        set_nn = self.get_nn(opcode)
        vr = self.registers["vr"]
        l = list(vr)
        #l[vreg] = int.from_bytes(set_nn)
        l[vreg] = set_nn
        nb = bytes(l)
        self.registers["vr"] = nb
    def set_i(self,opcode):
        set_nnn = self.get_nnn(opcode)
        #print("set is", set_nnn)
        self.registers["i"] = set_nnn
    def save_commit(self, result):
        if result:
            instruction, (h,l) = result
            checkpoint = instruction, {"high":h, "low":l}, {"hex_string": (hex(h), hex(l))} 
            self.instruction_history.append(checkpoint)
        else:
            self.instruction_history.append("Failed to parse")
    def draw(self, opcode):
        index = self.registers["i"]
        #print("drawing...")
        vr = self.registers["vr"]
        h,l = opcode
        vx = 0x0F & h
        vy = (0xF0 & l) >> 4
        l = list(vr)
        x = l[vx]
        y = l[vy]
        if x > 31: x = x % (screen_max_x - 1)
        if y > 63: y = y % (screen_max_y - 1)
        print(x,y, "XY HERE")
        if self.screen.draw(opcode,x,y,index,self.memory):
            l[0x0F] = 1
        else:
            l[0x0F] = 0
        self.registers["vr"] = bytes(l)
    def execute_instruction(self,result):
        self.save_commit(result)
        if result:
            instruction, opcode = result
            print(instruction)
            match instruction:
                case Instruction.CLEAR: return self.screen.clear()
                case Instruction.JMP: return self.set_pc(opcode)
                case Instruction.SET: return self.set_vreg(opcode)
                case Instruction.ADD: return self.v_add(opcode)
                case Instruction.SETI: return self.set_i(opcode)
                case Instruction.DRAW: return self.draw(opcode)
                case _: return
        else:
            raise Exception("unable to parse: ", result)
    def increment_pc(self):
        self.registers["pc"] = self.registers["pc"] + 2 # increment pc by two (each instruction is 16-bit)
        if self.registers["pc"] > 0xFFF:
            self.registers["pc"] = self.registers["pc"] % 0xFFF
    def write_history_to_json(self):
        print("writing history")
        js = json.dumps(self.instruction_history)
        with open("history.json", "w") as f:
            f.write(js)
    def run_cpu_loop(self):
        if self.memory:
            self.screen.init_screen()
            while self.run_program:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.run_program = False
                self.game_clock.tick(60)  # limits FPS to 60
                self.screen.update_screen()
                instruction = self.get_instruction() # decode opcode/fetch instruction
                self.increment_pc()
                self.execute_instruction(instruction) # execute instruction
                
        self.write_history_to_json()
    

if __name__ == "__main__":
    print("hellooo")
    a = Instruction.CLEAR
    path = "test.ch8"
    e = Emulator()
    e.read_rom(path)
    e.load_rom_to_memory()
    e.run_cpu_loop()
 

