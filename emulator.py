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
        
def is_clear(op):
    h = op.get_higher_byte().is_equal_to(0x00)
    l = op.get_lower_byte().is_equal_to(0xe0)
    return h and l

def is_jmp(op): return op.get_higher_byte().higher_nibble_is_equal_to(0x1)

def is_set(op): return op.get_higher_byte().higher_nibble_is_equal_to(0x6)

def is_add(op): return op.get_higher_byte().higher_nibble_is_equal_to(0x7)

def is_seti(op): return op.get_higher_byte().higher_nibble_is_equal_to(0xA)

def is_draw(op): return op.get_higher_byte().higher_nibble_is_equal_to(0xD)

DEBUG = False

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
    def set_i(self,opcode): self.registers["i"] = opcode.get_lower_NNN() # FYI, returns new instance
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
    def _check_pygame_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run_program = False
    def run_cpu_loop(self):
        if self.memory:
            self.screen.init_screen()
            while self.run_program:
                self._check_pygame_events()
                self.game_clock.tick(60) 
                self.screen.update_screen()
                opcode = self.get_instruction() # decode opcode/fetch instruction
                self.increment_pc()
                self.execute_instruction(opcode) # execute instruction
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No file path detected. Adieu!")
    else:
        e = Emulator()
        e.read_rom(sys.argv[1])
        e.load_rom_to_memory()
        e.run_cpu_loop()
 

