from ch8_types import Ch8Byte, Ch8Word

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
