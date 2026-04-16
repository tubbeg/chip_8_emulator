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
        if nr > 255 or nr < 0:
            # ordinarily, a constructor should never throw an exception
            raise Exception("bad number")
        self._byte = nr
    def add_byte(self,nr):
        if nr > 255 or nr < 0:
            raise Exception("bad number")
        n = nr & 0xFF
        self._byte = (self._byte + n) % 0xFF
    def set_value(self,nr):
        n = nr & 0xFF
        self._byte = n % 0xFF
    def get_byte_value(self):
        return self._byte
    def get_lower_nibble(self):
        return self._byte & 0x0F
    def get_higher_nibble(self):
        return self._byte >> 4
    def lower_nibble_is_equal_to(self,nr):
        return self.get_lower_nibble() == nr
    def higher_nibble_is_equal_to(self,nr):
        return self.get_higher_nibble() == nr
    def is_equal_to(self,nr): return self._byte == nr
    def increment(self):
        self._byte += 1
        if self._byte > 0xFF:
            self._byte = 0
            return True # carry overflow
        return False
    def bit_is_set(self,nth):
        return (self._byte & (1<<nth)) > 0

class Ch8Word():
    def __init__(self) -> None:
        self.high = None
        self.low = None
    def init_word(self, high, low):
        # essentially an additional constructor that can crash :)
        if not isinstance(high, Ch8Byte) or not isinstance(low, Ch8Byte):
            raise Exception("not initialized")
        self.high = high
        self.low = low
        return self
    def get_higher_byte(self): return self.high
    def get_lower_byte(self): return self.low
    def _bytes_to_word(self,high,low):
        h = high << 8
        return h | low
    def get_word_value(self):
        if self.high and self.low:
            high = self.high.get_byte_value()
            low = self.low.get_byte_value()
            return self._bytes_to_word(high,low)
        raise Exception("not initialized")
    def increment(self):
        if self.high and self.low:
            if self.low.increment():
                return self.high.increment()
            return False
        raise Exception("not initialized")
    def get_low_byte_higher_nibble(self):
        if self.low:
            return self.low.get_higher_nibble()
        raise Exception()
    def get_low_byte_lower_nibble(self):
        if self.low:
            return self.low.get_lower_nibble()
        raise Exception()
    def get_high_byte_lower_nibble(self):
        if self.high:
            return self.high.get_lower_nibble()
        raise Exception()
    def get_lower_NN(self):
        if self.low: return self.low.get_byte_value()
        raise Exception("not initialized")
    def get_lower_NNN(self):
        if self.high and self.low:
            hbln = self.high.get_lower_nibble()
            lb = self.low.get_byte_value()
            return Ch8Word().init_word(Ch8Byte(hbln), Ch8Byte(lb))
        raise Exception("not initialized")
        
def is_clear(op):
    h = op.get_higher_byte().is_equal_to(0x00)
    l = op.get_lower_byte().is_equal_to(0xe0)
    return h and l

def is_jmp(op): return op.get_higher_byte().higher_nibble_is_equal_to(0x1)

def is_set(op): return op.get_higher_byte().higher_nibble_is_equal_to(0x6)

def is_add(op): return op.get_higher_byte().higher_nibble_is_equal_to(0x7)

def is_seti(op): return op.get_higher_byte().higher_nibble_is_equal_to(0xA)

def is_draw(op): return op.get_higher_byte().higher_nibble_is_equal_to(0xD)

# 4096 bytes memory with first 512 bytes reserved
# big endian
# 16b v registers, one program counter (16-bit), one memory (index) register 12 bit

class Memory():
    def __init__(self, ba) -> None:
        l = []
        for i in range(0,0x1000):
            if i >= 0x200 and i < len(ba) + 0x200:
                l.append(Ch8Byte(ba[i - 0x200]))
            else:
                l.append(Ch8Byte(0))
        self._memory = l
    def try_get_index_memory(self, index, number_of_bytes):
            try:
                return self._memory[index:index + number_of_bytes]
            except:
                raise Exception()
    def try_get_opcode_memory(self,pc):
        try:
            nr = pc.get_word_value()
            high = self._memory[nr]
            low = self._memory[nr + 1]
            return Ch8Word().init_word(high,low)
        except:
            raise Exception("pc at: ", type(pc))

screen_max_x = 32 #  8x8 bits
screen_max_y = 64 # 8x4 bits

DEBUG = False

def default_screen():
    screen = {}
    for i in range(0,screen_max_y):
        for j in range(0,screen_max_x):
            s = "k" + str(i) + str(j)
            screen[s] = False
    return screen

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
        for i in range(0,screen_max_x):
            for j in range(0,screen_max_y):
                self.draw_pygame_pixel(y,x, 7, 7, self._screen[self.get_key_str(j,i)])
                y += 8
            y = y_init
            x += 8
        pygame.display.flip()
    def get_key_str(self,x,y):
        return "k" + str(x) + str(y)
    def init_screen(self):
        self.game_screen = pygame.display.set_mode((800, 600))
        self._screen = default_screen()
    def clear(self):
        self._screen = default_screen()
    def xor_bit(self,x,y, bit):
        current = self._screen[self.get_key_str(x,y)]
        next = (current and not bit) or (not current and bit) # xor operation
        self._screen[self.get_key_str(x,y)] = next
        return not next and current # carry flag
    def draw_byte(self, x,y, byte):
        x_pos = x
        f = False
        l = [byte.bit_is_set(i) for i in range(0,8)]
        for bit in list(reversed(l)):
            print("Drawing coordinate", x_pos,y)
            if self.xor_bit(x_pos,y,bit): f = True
            x_pos += 1
        return f
    def draw(self, mem, x, y):
        f = False
        y_pos = y
        for b in mem:
            if self.draw_byte(x,y_pos,b): f = True
            y_pos += 1
        if DEBUG:
            print("===========================================")
            input("Pause for exec")
        return f
        # which bits are supposed to be true or false?
        # it's determined by the memory pointed by the index register


class Emulator():
    def __init__(self) -> None:
        pygame.init()
        self.game_clock = pygame.time.Clock()
        self.memory = None
        self.screen = Screen()
        self.registers = {
            "vr":[Ch8Byte(0) for i in range(0,16)],
            "i":Ch8Word().init_word(Ch8Byte(0), Ch8Byte(0)), # index
            "pc":Ch8Word().init_word(Ch8Byte(0x02), Ch8Byte(0x00))  # should actually be 12bit
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
            if opcode := self.memory.try_get_opcode_memory(self.registers["pc"]):
                if is_clear(opcode):return Instruction.CLEAR,opcode
                if is_jmp(opcode): return Instruction.JMP,opcode
                if is_set(opcode): return Instruction.SET,opcode
                if is_add(opcode): return Instruction.ADD,opcode
                if is_seti(opcode): return Instruction.SETI,opcode
                if is_draw(opcode): return Instruction.DRAW,opcode
        return None      
    def set_pc(self, opcode): self.registers["pc"] = opcode.get_lower_NNN()
    def v_add(self, opcode):
        # does not set carry flag
        vreg = opcode.get_high_byte_lower_nibble()
        self.registers["vr"][vreg].add_byte(opcode.get_lower_NN())
    def set_vreg(self,opcode):
        vreg = opcode.get_high_byte_lower_nibble()
        self.registers["vr"][vreg] = Ch8Byte(opcode.get_lower_NN())
    def set_i(self,opcode): self.registers["i"] = opcode.get_lower_NNN() # fyi, returns new instance
    def save_commit(self, result): 
        if result:
            pass
        else:
            self.instruction_history.append("Failed to parse")
    def set_carry_flag(self):
        self.registers["vr"][0x0F] = Ch8Byte(1)
    def reset_carry_flag(self):
        self.registers["vr"][0x0F] = Ch8Byte(0)
    def draw(self, opcode):
        if self.memory:
            index = self.registers["i"].get_word_value()
            vx = opcode.get_high_byte_lower_nibble()
            vy = opcode.get_low_byte_higher_nibble()
            x = self.registers["vr"][vx].get_byte_value()
            y = self.registers["vr"][vy].get_byte_value()
            #if x > (screen_max_y - 1): x = x % (screen_max_y - 1)
            #if y > (screen_max_x - 1): y = y % (screen_max_x - 1)
            number_of_bytes = opcode.get_low_byte_lower_nibble()
            if mem := self.memory.try_get_index_memory(index, number_of_bytes):
                if self.screen.draw(mem,x,y):
                    self.set_carry_flag()
                else:
                    self.reset_carry_flag()
                return
        raise Exception("no memory")
    def execute_instruction(self,result):
        self.save_commit(result)
        if result:
            instruction, opcode = result
            match instruction:
                case Instruction.CLEAR: return self.screen.clear()
                case Instruction.JMP: return self.set_pc(opcode)
                case Instruction.SET: return self.set_vreg(opcode)
                case Instruction.ADD: return self.v_add(opcode)
                case Instruction.SETI: return self.set_i(opcode)
                case Instruction.DRAW: return self.draw(opcode)
                case _: return
        else:
            return
    def increment_pc(self):
        self.registers["pc"].increment()
        self.registers["pc"].increment()
        if self.registers["pc"].get_word_value() > 0xFFF: # out of memory
            self.registers["pc"] = Ch8Word().init_word(Ch8Byte(0), Ch8Byte(0))
    def run_cpu_loop(self):
        if self.memory:
            self.screen.init_screen()
            while self.run_program:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.run_program = False
                self.game_clock.tick(60) 
                self.screen.update_screen()
                instruction = self.get_instruction() # decode opcode/fetch instruction
                self.increment_pc()
                self.execute_instruction(instruction) # execute instruction
    

if __name__ == "__main__":
    a = Instruction.CLEAR
    path = "test.ch8"
    e = Emulator()
    e.read_rom(path)
    e.load_rom_to_memory()
    e.run_cpu_loop()
 

