
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
    def add_with_carry(self,nr):
        self._byte += nr
        carry_flag = self._byte > 255 or self._byte < 0
        self._byte = self._byte % 255
        return int(carry_flag)
    def sub_with_carry(self,nr):
        self._byte -= nr
        carry_flag = self._byte > 255 or self._byte < 0
        self._byte = self._byte % 255
        return int(not carry_flag) # carry flag is set to zero if vx >= vy
    def sub_rev_with_carry(self,nr):
        self._byte = nr - self._byte # subtracts -> vx = vy - vx
        carry_flag = self._byte > 255 or self._byte < 0
        self._byte = self._byte % 255
        return int(not carry_flag)
    def bit_or(self, nr):
        self._byte |= nr
    def bit_and(self,nr):
        self._byte &= nr
    def bit_xor(self, nr):
        self._byte ^= nr
    def shift_right(self):
        lb = self.bit_is_set(0) # least significant bit
        self._byte = self._byte >> 1
        return int(lb)
    def shift_left(self):
        mb = self.bit_is_set(7) # most significant bit
        self._byte = self._byte << 1
        return int(mb)

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
        if self.low: return self.low.get_byte_value() #RETURNS A VALUE, NOT AN OBJECT!!
        raise Exception("not initialized")
    def get_lower_NNN(self):
        if self.high and self.low:
            hbln = self.high.get_lower_nibble()
            lb = self.low.get_byte_value()
            return Ch8Word().init_word(Ch8Byte(hbln), Ch8Byte(lb))
        raise Exception("not initialized")