import pygame
import json

screen_max_x = 32 #  8x8 bits
screen_max_y = 64 # 8x4 bits


def default_screen():
    screen = {}
    for i in range(0,screen_max_y):
        for j in range(0,screen_max_x):
            s = "k" + str(i) + ";" + str(j)
            screen[s] = False
    return screen

class Screen():
    def __init__(self, debug=False) -> None:
        self._debug = debug
    def save_bits(self):
        if self._screen:
            l = []
            for k in self._screen:
                if self._screen[k]:
                    l.append(k)
            with open("bits.json", "w") as f:
                f.write(json.dumps(l))
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
        return "k" + str(x) + ";" + str(y)
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
        for bit in list(reversed(l)):   #NOTE!! VERY IMPORTANT TO START DRAWING FROM THE MOST SIGNIFICANT BIT!!!!
            if self._debug:
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
        if self._debug:
            print("===========================================")
            input("Pause for exec")
        return f
        # which bits are supposed to be true or false?
        # it's determined by the memory pointed by the index register

