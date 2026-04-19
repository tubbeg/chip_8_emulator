
## CHIP-8 Emulator


![image info](./demo.webm.mp4)

### What is this?

This is an emulator for the CHIP-8. Technically speaking, it's not a true emulator since it does not emulate physical hardware. So it's actually closer to an interpreter.

![image info](./example_image.png)

### What can it do?

Many ROMs are already working despite the fact that not every instruction has been implemented.

It can the run the 'IBM Logo' program. You can find the program by searching 'IBM Logo CHIP-8' in your favourite search engine.

### What's missing?

Sound, input, and delay timers remain to be implemented.
s
### How do I run this?

1. Install the latest version of python and git
2. Open your favourite Linux terminal and clone this repository via: ``git clone git@github.com:tubbeg/chip_8_emulator.git``
3. Run ``cd chip_8_emulator``
4. Run ``python -m pip install requirements.txt``
5. Run ``python emulator.py my/path/to/chip8/file.ch8``
6. Enjoy!