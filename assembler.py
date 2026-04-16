import emulator as e


## WIP!

class Assembler():
    def __init__(self) -> None:
        pass
    def instructions_to_bytes(self, instructions):
        code = []
        for ins in instructions:
            match ins:
                case _: code.append(e.Ch8Byte(0))
        return code
    def assemble(self):
        pass


