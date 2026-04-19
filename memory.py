from ch8_types import Ch8Byte, Ch8Word
# 4096 bytes memory with first 512 bytes reserved
# big endian
# 16b v registers, one program counter (16-bit), one memory (index) register 12 bit

# font data
zero = [0xF0,0x90,0x90,0x90,0xF0]
one = [0x20, 0x60, 0x20, 0x20, 0x70]
two = [0x20, 0x60, 0x20, 0x20, 0x70]
three = [0xF0, 0x10, 0xF0, 0x80, 0xF0]
four = [0x90, 0x90, 0xF0, 0x10, 0x10]
five = [0xF0, 0x80, 0xF0, 0x10, 0xF0]
six = [0xF0, 0x80, 0xF0, 0x90, 0xF0]
seven = [0xF0, 0x10, 0x20, 0x40, 0x40]
eight = [0xF0, 0x90, 0xF0, 0x90, 0xF0]
nine = [0xF0, 0x90, 0xF0, 0x10, 0xF0]
a = [0xF0, 0x90, 0xF0, 0x90, 0x90]
b = [0xE0, 0x90, 0xE0, 0x90, 0xE0]
c = [0xF0, 0x80, 0x80, 0x80, 0xF0]
d = [0xE0, 0x90, 0x90, 0x90, 0xE0]
e = [0xF0, 0x80, 0xF0, 0x80, 0xF0]
f = [0xF0, 0x80, 0xF0, 0x80, 0x80]
fonts = [zero,one,two,three,four,five,six,seven,eight,nine,a,b,c,d,e,f]

class Memory():
    def __init__(self, ba) -> None:
        self._memory = []
        for i in range(0,0x1000):
            if i >= 0x200 and i < len(ba) + 0x200:
                self._memory.append(Ch8Byte(ba[i - 0x200]))
            else:
                self._memory.append(Ch8Byte(0))
        font_start_address = 0x50
        mi = font_start_address
        for f in fonts:
            for b in f:
                self._memory[mi] = Ch8Byte(b)
                mi += 1
    def try_get_index_memory(self, index, number_of_bytes):
        res = self._memory[index:index + number_of_bytes]
        return res
    def try_get_opcode_memory(self,pc):
        try:
            nr = pc.get_word_value()
            high = self._memory[nr]
            low = self._memory[nr + 1]
            return Ch8Word().init_word(high,low)
        except:
            raise Exception("pc at: ", type(pc))
    def try_get_registers_memory(self, index):
        try:
            return self._memory[index:index + 0x0F]
        except:
            raise Exception(index, "index")
    def try_store_registers_memory(self, index, registers):
        try:
            i = 0
            for r in registers:
                self._memory[index + i] = r
                i += 1
            return None
        except:
            raise Exception(index, "index")
    def try_store_bcd(self,index, bcd):
        try:
            hundreds = (bcd - (bcd % 100)) / 100
            tens = ((bcd % 100) - (bcd % 10)) / 10
            ones = bcd % 10
            self._memory[index] = Ch8Byte(int(hundreds))
            self._memory[index + 1] = Ch8Byte(int(tens))
            self._memory[index + 2] = Ch8Byte(int(ones))
            return None
        except:
            raise Exception(index, "index")

