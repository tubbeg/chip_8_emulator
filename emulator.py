from enum import Enum
import threading
import json
import time
import csv
import sys
import pygame
from instructions import Instruction
from ch8_types import Ch8Byte, Ch8Word
from memory import Memory
from screen import Screen
import random
import math

input_map = {
    0x0 : pygame.K_SPACE,
    0x1 : pygame.K_KP1,
    0x2 : pygame.K_KP2,
    0x3 : pygame.K_KP3,
    0x4 : pygame.K_KP4,
    0x5 : pygame.K_KP5,
    0x6 : pygame.K_KP6,
    0x7 : pygame.K_KP7,
    0x8 : pygame.K_KP8,
    0x9 : pygame.K_KP9,
    0xA : pygame.K_q,
    0xB : pygame.K_w,
    0xC : pygame.K_e,
    0xD : pygame.K_r,
    0xE : pygame.K_t,
    0xF : pygame.K_y,
}

def is_clear(op):
    h = op.get_higher_byte().is_equal_to(0x00)
    l = op.get_lower_byte().is_equal_to(0xe0)
    return h and l

def last_nibble_is_nr(op,nr):
    return op.get_lower_byte().lower_nibble_is_equal_to(nr)

def last_nibble_is_zero(op):
    return last_nibble_is_nr(op,0x0)

def last_nibble_is_one(op):
    return last_nibble_is_nr(op,0x1)

def last_nibble_is_two(op):
    return last_nibble_is_nr(op,0x2)

def last_nibble_is_three(op):
    return last_nibble_is_nr(op,0x3)

def last_nibble_is_four(op):
    return last_nibble_is_nr(op,0x4)

def last_nibble_is_five(op):
    return last_nibble_is_nr(op,0x5)

def last_nibble_is_six(op):
    return last_nibble_is_nr(op,0x6)

def last_nibble_is_seven(op):
    return last_nibble_is_nr(op,0x7)

def last_nibble_is_eight(op):
    return last_nibble_is_nr(op,0x8)

def last_nibble_is_nine(op):
    return last_nibble_is_nr(op,0x9)

def last_nibble_is_e(op):
    return last_nibble_is_nr(op,0xE)

def last_nibble_is_a(op):
    return last_nibble_is_nr(op,0xA)

def is_jmp(op): return op.get_higher_byte().higher_nibble_is_equal_to(0x1)

def is_if(op): return op.get_higher_byte().higher_nibble_is_equal_to(0x3)

def is_ifnot(op): return op.get_higher_byte().higher_nibble_is_equal_to(0x4)

def is_ifv(op):
    h = op.get_higher_byte().higher_nibble_is_equal_to(0x5)
    return h and last_nibble_is_zero(op)

def is_set(op): return op.get_higher_byte().higher_nibble_is_equal_to(0x6)

def is_add(op): return op.get_higher_byte().higher_nibble_is_equal_to(0x7)

def first_nibble_is_eight(op): return op.get_higher_byte().higher_nibble_is_equal_to(0x8)

def first_nibble_is_f(op): return op.get_higher_byte().higher_nibble_is_equal_to(0xF)

def is_setv(op): return first_nibble_is_eight(op) and last_nibble_is_zero(op)

def is_seti(op): return op.get_higher_byte().higher_nibble_is_equal_to(0xA)

def is_draw(op): return op.get_higher_byte().higher_nibble_is_equal_to(0xD)

def is_or(op): return first_nibble_is_eight(op) and last_nibble_is_one(op)

def is_and(op): return first_nibble_is_eight(op) and last_nibble_is_two(op)

def is_xor(op): return first_nibble_is_eight(op) and last_nibble_is_three(op)

def is_add_with_carry(op): return first_nibble_is_eight(op) and last_nibble_is_four(op)

def is_sub_with_carry(op): return first_nibble_is_eight(op) and last_nibble_is_five(op)

def is_shift_right(op): return first_nibble_is_eight(op) and last_nibble_is_six(op)

def is_sbc_rev(op): return first_nibble_is_eight(op) and last_nibble_is_seven(op)

def is_shift_left(op): return first_nibble_is_eight(op) and last_nibble_is_e(op)

def is_ifnot_v(op):
    h = op.get_higher_byte().higher_nibble_is_equal_to(0x9)
    return h and last_nibble_is_zero(op)

def is_rjmp(op): return op.get_higher_byte().higher_nibble_is_equal_to(0xB)

def is_rand(op): return op.get_higher_byte().higher_nibble_is_equal_to(0xC)

def is_if_key(op):
    h = op.get_higher_byte().higher_nibble_is_equal_to(0xe)
    lhn = op.get_lower_byte().higher_nibble_is_equal_to(0x9)
    ret = h and lhn and last_nibble_is_e(op)
    return ret

def is_ifnot_key(op):
    h = op.get_higher_byte().higher_nibble_is_equal_to(0xe)
    lhn = op.get_lower_byte().higher_nibble_is_equal_to(0xa)
    return h and lhn and last_nibble_is_one(op)

def is_get_delay(op):
    lhn = op.get_lower_byte().higher_nibble_is_equal_to(0x0)
    return first_nibble_is_f(op) and lhn and last_nibble_is_seven(op)

def is_get_key(op):
    lhn = op.get_lower_byte().higher_nibble_is_equal_to(0x0)
    return first_nibble_is_f(op) and lhn and last_nibble_is_a(op)

def is_set_delay(op):
    lhn = op.get_lower_byte().higher_nibble_is_equal_to(0x1)
    return first_nibble_is_f(op) and lhn and last_nibble_is_five(op)

def is_sound(op):
    lhn = op.get_lower_byte().higher_nibble_is_equal_to(0x1)
    return first_nibble_is_f(op) and lhn and last_nibble_is_eight(op)

def is_add_i(op):
    lhn = op.get_lower_byte().higher_nibble_is_equal_to(0x1)
    return first_nibble_is_f(op) and lhn and last_nibble_is_e(op)

def is_setiv(op):
    lhn = op.get_lower_byte().higher_nibble_is_equal_to(0x2)
    return first_nibble_is_f(op) and lhn and last_nibble_is_nine(op)

def is_bcd(op): 
    lhn = op.get_lower_byte().higher_nibble_is_equal_to(0x3)
    return first_nibble_is_f(op) and lhn and last_nibble_is_three(op)

def is_store(op): 
    lhn = op.get_lower_byte().higher_nibble_is_equal_to(0x5)
    return first_nibble_is_f(op) and lhn and last_nibble_is_five(op)

def is_reload(op): 
    lhn = op.get_lower_byte().higher_nibble_is_equal_to(0x6)
    return first_nibble_is_f(op) and lhn and last_nibble_is_five(op)

def is_sbr(op): return op.get_higher_byte().higher_nibble_is_equal_to(0x2)

def is_ret(op): return op.get_word_value() == 0x00ee

update_pygame_const = 10

DEBUG = False

# arithmetic logic unit, the basis of every processor
class ALU():
    pass


class Emulator(ALU):
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
        self.update_freq = update_pygame_const
        self.input_keys = []
        self.stack = []
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
                if is_if(opcode): return Instruction.IF,opcode
                if is_ifv(opcode): return Instruction.IFV,opcode
                if is_ifnot(opcode): return Instruction.IFNOT,opcode
                if is_set(opcode): return Instruction.SET,opcode
                if is_add(opcode): return Instruction.ADD,opcode
                if is_setv(opcode): return Instruction.SETV,opcode
                if is_seti(opcode): return Instruction.SETI,opcode
                if is_draw(opcode): return Instruction.DRAW,opcode
                if is_and(opcode): return Instruction.AND, opcode
                if is_or(opcode): return Instruction.OR, opcode
                if is_xor(opcode): return Instruction.XOR, opcode
                if is_add_with_carry(opcode): return Instruction.ADC, opcode
                if is_sub_with_carry(opcode): return Instruction.SBC, opcode
                if is_shift_right(opcode): return Instruction.SHIFTR, opcode
                if is_sbc_rev(opcode): return Instruction.SBCREV, opcode
                if is_shift_left(opcode): return Instruction.SHIFTL, opcode
                if is_ifnot_v(opcode): return Instruction.IFNOTV, opcode
                if is_rjmp(opcode): return Instruction.RJMP, opcode
                if is_rand(opcode): return Instruction.RAND, opcode
                if is_if_key(opcode): return Instruction.IFKEY, opcode
                if is_ifnot_key(opcode): return Instruction.IFNKEY, opcode
                if is_get_delay(opcode): return Instruction.GDELAY, opcode
                if is_get_key(opcode): return Instruction.GKEY, opcode
                if is_set_delay(opcode): return Instruction.SDELAY, opcode
                if is_sound(opcode): return Instruction.SOUND, opcode
                if is_add_i(opcode): return Instruction.ADDI, opcode
                if is_bcd(opcode): return Instruction.BCD, opcode
                if is_store(opcode): return Instruction.STORE, opcode
                if is_reload(opcode): return Instruction.RELOAD, opcode
                if is_setiv(opcode): return Instruction.SETIV, opcode
                if is_sbr(opcode): return Instruction.SBR, opcode
                if is_ret(opcode): return Instruction.RET, opcode
            raise Exception(opcode.get_word_value())
        return None
    def set_pc(self, opcode): self.registers["pc"] = opcode.get_lower_NNN()
    def set_relative_pc(self, opcode):
        nnn = opcode.get_lower_NNN()
        self.registers["pc"] = nnn.add_ch8_byte(self.registers["pc"][0x00])
    def v_add(self, opcode):
        # does not set carry flag
        vreg = opcode.get_high_byte_lower_nibble()
        self.registers["vr"][vreg].add_byte(opcode.get_lower_NN())
    def add_with_carry(self, opcode):
        vx = opcode.get_high_byte_lower_nibble()
        vy = opcode.get_low_byte_higher_nibble()
        vreg_y = self.registers["vr"][vy]
        carry_flag = self.registers["vr"][vx].add_with_carry(vreg_y.get_byte_value())
        self.registers["vr"][0x0F - 1] = Ch8Byte(carry_flag)
    def sub_with_carry(self, opcode):
        vx = opcode.get_high_byte_lower_nibble()
        vy = opcode.get_low_byte_higher_nibble()
        vreg_y = self.registers["vr"][vy]
        carry_flag = self.registers["vr"][vx].sub_with_carry(vreg_y.get_byte_value())
        self.registers["vr"][0x0F - 1] = Ch8Byte(carry_flag)
    def sub_reverse_with_carry(self, opcode):
        vx = opcode.get_high_byte_lower_nibble()
        vy = opcode.get_low_byte_higher_nibble()
        vreg_y = self.registers["vr"][vy]
        carry_flag = self.registers["vr"][vx].sub_rev_with_carry(vreg_y.get_byte_value())
        self.registers["vr"][0x0F - 1] = Ch8Byte(carry_flag)
    def set_vreg(self,opcode):
        vreg = opcode.get_high_byte_lower_nibble()
        self.registers["vr"][vreg] = Ch8Byte(opcode.get_lower_NN())
    def set_vreg_from_vreg(self,opcode):
        vreg = opcode.get_high_byte_lower_nibble()
        self.registers["vr"][vreg] = Ch8Byte(opcode.get_lower_NN())
    def set_i(self,opcode): self.registers["i"] = opcode.get_lower_NNN() # FYI, returns new instance
    def set_carry_flag(self):
        self.registers["vr"][0x0F - 1] = Ch8Byte(1)
    def reset_carry_flag(self):
        self.registers["vr"][0x0F - 1] = Ch8Byte(0)
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
        if result:
            instruction, opcode = result
            if DEBUG:
                print(instruction)
            match instruction:
                case Instruction.CLEAR: return self.screen.clear()
                case Instruction.JMP: return self.set_pc(opcode)
                case Instruction.IF: return self.skip_if_opcode(opcode)
                case Instruction.IFNOT: return self.skip_if_not_opcode(opcode)
                case Instruction.IFV: return self.skip_if_v_opcode(opcode)
                case Instruction.SET: return self.set_vreg(opcode)
                case Instruction.ADD: return self.v_add(opcode)
                case Instruction.SETV: return self.set_v(opcode)
                case Instruction.SETI: return self.set_i(opcode)
                case Instruction.DRAW: return self.draw(opcode)
                case Instruction.OR: return self.bit_or(opcode)
                case Instruction.AND: return self.bit_and(opcode)
                case Instruction.XOR: return self.bit_xor(opcode)
                case Instruction.ADC: return self.add_with_carry(opcode)
                case Instruction.SBC: return self.sub_with_carry(opcode)
                case Instruction.SHIFTR: return self.shift_right(opcode)
                case Instruction.SBCREV: return self.sub_reverse_with_carry(opcode)
                case Instruction.SHIFTR: return self.shift_left(opcode)
                case Instruction.IFNOTV: return self.skip_ifnot_v(opcode)
                case Instruction.RJMP: return self.set_relative_pc(opcode)
                case Instruction.RAND: return self.rand(opcode)
                case Instruction.IFKEY: return self.ifkey(opcode)
                case Instruction.IFNKEY: return self.ifnkey(opcode)
                case Instruction.GDELAY: return self.get_delay(opcode)
                case Instruction.GKEY: return self.get_key(opcode)
                case Instruction.SDELAY: return self.set_delay(opcode)
                case Instruction.SOUND: return self.set_sound(opcode)
                case Instruction.ADDI: return self.add_i(opcode)
                case Instruction.BCD: return self.bcd(opcode)
                case Instruction.STORE: return self.store(opcode)
                case Instruction.RELOAD: return self.reload(opcode)
                case Instruction.SETIV: return self.setiv(opcode)
                case Instruction.SBR: return self.call_subroutine(opcode)
                case Instruction.RET: return self.return_subroutine(opcode)
                case _: return None
        else:
            return None
    def return_subroutine(self,_):
        value = self.stack.pop()
        high, low = Ch8Byte(value >> 8), Ch8Byte(value & 0xFF)
        self.registers["pc"] = Ch8Word().init_word(high,low)
    def call_subroutine(self,opcode):
        self.stack.append(self.registers["pc"].get_word_value())
        self.registers["pc"] = opcode.get_lower_NNN()
    def setiv(self,opcode):
        raise Exception("NOT YET IMPLEMENTED")
    def bcd(self,opcode):
        raise Exception("NOT YET IMPLEMENTED")
    def store(self,opcode):
        if self.memory:
            index = self.registers["i"].get_word_value()
            self.memory.try_store_registers_memory(index, self.registers["vr"])
            return None
        raise Exception("Not initialized")
    def reload(self,opcode):
        if self.memory:
            index = self.registers["i"].get_word_value()
            self.registers["vr"] = self.memory.try_get_registers_memory(index)
            return None
        raise Exception("Not initialized")
    def add_i(self,opcode):
        vx = opcode.get_high_byte_lower_nibble()
        self.registers["i"].add_ch8_byte(self.registers["vr"][vx])
    def set_sound(self,opcode):
        raise Exception("NOT YET IMPLEMENTED")
    def set_delay(self,opcode):
        raise Exception("NOT YET IMPLEMENTED")
    def get_key(self,opcode):
        # timers will continue in the background here
        raise Exception("NOT YET IMPLEMENTED")
    def get_delay(self,opcode):
        # should timers update at the same rate as the pygame screen?
        raise Exception("NOT YET IMPLEMENTED")
    def ifkey(self,opcode):
        # does not seem like the list is retaining the keys for very long so I'm wondering
        # how this is going to work
        try:
            vx = opcode.get_high_byte_lower_nibble()
            v = self.registers["vr"][vx].to_byte_value()
            k = input_map[v]
            for ik in self.input_keys:
                if ik == k:
                    self.increment_pc()
                    return None
            return None
        except:
            return None
    def ifnkey(self,opcode):
        try:
            vx = opcode.get_high_byte_lower_nibble()
            v = self.registers["vr"][vx].to_byte_value()
            k = input_map[v]
            for ik in self.input_keys:
                if not ik == k:
                    self.increment_pc()
                    return None
            return None
        except:
            return None
    def rand(self,opcode):
        vx = opcode.get_high_byte_lower_nibble()
        nn = opcode.get_lower_NN()
        rand = math.floor(random.random() * 255)
        self.registers["vr"][vx] = Ch8Byte(nn & rand)
    def increment_pc(self):
        self.registers["pc"].increment()
        self.registers["pc"].increment()
        if self.registers["pc"].get_word_value() > 0xFFF: # out of memory
            self.registers["pc"] = Ch8Word().init_word(Ch8Byte(0), Ch8Byte(0))
    def skip_if_opcode(self, opcode):
        vx = opcode.get_high_byte_lower_nibble()
        nn = opcode.get_lower_NN()
        if self.registers["vr"][vx].is_equal_to(nn): #if -> skip next ins
            self.increment_pc()
    def skip_if_not_opcode(self, opcode):
        vx = opcode.get_high_byte_lower_nibble()
        nn = opcode.get_lower_NN()
        if not self.registers["vr"][vx - 1].is_equal_to(nn): #if not -> skip next ins
            self.increment_pc()
    def skip_if_v_opcode(self,opcode):
        vx = opcode.get_high_byte_lower_nibble()
        vy = opcode.get_low_byte_higher_nibble()
        vreg_x,vreg_y = self.registers["vr"][vx],self.registers["vr"][vy]
        if vreg_x.is_equal_to(vreg_y.get_byte_value()):
            self.increment_pc()
    def skip_ifnot_v(self,opcode):
        vx = opcode.get_high_byte_lower_nibble()
        vy = opcode.get_low_byte_higher_nibble()
        vreg_x,vreg_y = self.registers["vr"][vx],self.registers["vr"][vy]
        if not vreg_x.is_equal_to(vreg_y.get_byte_value()):
            self.increment_pc()
    def set_vx_fn_vy(self,opcode, fn):
        vx = opcode.get_high_byte_lower_nibble()
        vy = opcode.get_low_byte_higher_nibble()
        val_y = self.registers["vr"][vy].get_byte_value()
        val_x = self.registers["vr"][vx].get_byte_value()
        self.registers["vr"][vx] = fn(val_x,val_y)
    def set_v(self, opcode):
        vx = opcode.get_high_byte_lower_nibble()
        vy = opcode.get_low_byte_higher_nibble()
        val_y = self.registers["vr"][vy].get_byte_value()
        self.registers["vr"][vx] = Ch8Byte(val_y)
    def bit_or(self,opcode):
        vx = opcode.get_high_byte_lower_nibble()
        vy = opcode.get_low_byte_higher_nibble()
        self.registers["vr"][vx].bit_or(self.registers["vr"][vy].get_byte_value())
    def bit_and(self,opcode):
        vx = opcode.get_high_byte_lower_nibble()
        vy = opcode.get_low_byte_higher_nibble()
        self.registers["vr"][vx].bit_and(self.registers["vr"][vy].get_byte_value())
    def bit_xor(self,opcode):
        vx = opcode.get_high_byte_lower_nibble()
        vy = opcode.get_low_byte_higher_nibble()
        self.registers["vr"][vx].bit_xor(self.registers["vr"][vy].get_byte_value())
    def shift_right(self, opcode):
        vx = opcode.get_high_byte_lower_nibble()
        lb = self.registers["vr"][vx].shift_right()
        self.registers["vr"][0x0F - 1] = Ch8Byte(lb)
    def shift_left(self, opcode):
        vx = opcode.get_high_byte_lower_nibble()
        mb = self.registers["vr"][vx].shift_left()
        self.registers["vr"][0x0F - 1] = Ch8Byte(mb)
    def set_input_keys(self,event):
        kl = []
        if event.type == pygame.KEYDOWN:
            kl.append(event.key)
        if event.type == pygame.KEYUP:
            for kd in self.input_keys:
                if not kd == event.key:
                    kl.append(kd)
        self.input_keys = kl
    def check_pygame_events(self):
        for event in pygame.event.get():
            self.set_input_keys(event)
            if event.type == pygame.QUIT:
                self.run_program = False
    def update_pygame(self):
        self.check_pygame_events()
        self.screen.update_screen()
        self.update_freq -= -1
        if self.update_freq < 1:
            dt = self.game_clock.tick(60) 
            self.update_freq = update_pygame_const
    def run_cpu_loop(self):
        if self.memory:
            self.screen.init_screen()
            while self.run_program:
                opcode = self.get_instruction() # decode opcode/fetch instruction
                self.increment_pc()
                self.execute_instruction(opcode) # execute instruction
                self.update_pygame()
            #self.screen.save_bits()
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No file path detected. Adieu!")
    else:
        e = Emulator()
        e.read_rom(sys.argv[1])
        e.load_rom_to_memory()
        e.run_cpu_loop()
 

