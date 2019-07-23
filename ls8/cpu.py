"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # memory to hold 256 bytes of memory
        self.ram = [00000000] * 256
        # 8 genreal purpose registers
        self.reg = [0] * 8
        # initialize PC that will be incremented
        self.pc = 0

    def ram_read(self, MAR):
        """accept the address to read and return the value stored there
        MAR = Memory ADdress Register"""
        return self.ram[MAR]

    def ram_write(self, MDR, MAR):
        """accepts a value to write, and the address to write it to.
        MDR = Memory Data Register, MAR = Memory ADdress Register"""
        self.ram[MAR] = MDR

    def load(self):
        """Load a program into memory."""
        address = 0

        if len(sys.argv) != 2:
            print(f"usage: {sys.argv[0]} [file]")
            sys.exit(1)

        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    # find first part of instructions, before the comment
                    number = line.split('#')[0]
                    # replace all \n with empty space
                    number = number.replace('\n', '')
                    # remove any empty space before or after number
                    number = number.strip()

                    # ignoring blank lines, convert binary to int and store in ram
                    if number is not '':
                        number = int(number, 2)
                        # add to memory
                        self.ram[address] = number
                        address += 1
        except FileNotFoundError:
            print(f"{sys.argv[0]}: File does not exist")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        # operations handled within ALU
        MUL = 0b10100010

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == MUL:
            mult1 = self.reg[reg_a]
            mult2 = self.reg[reg_b]
            res = mult1 * mult2
            self.reg[reg_a] = res
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        # operations handled without ALU
        LDI = 0b10000010
        PRN = 0b01000111
        HLT = 0b00000001

        running = True

        while running:
            # holds a copy of the currently executing 8-bit instruction
            ir = self.ram[self.pc]

            # stores operands a and b which can be 1 or 2 bytes ahead of instruction byte, or nonexistent
            operand_a = self.ram_read(self.pc+1)
            operand_b = self.ram_read(self.pc+2)

            # mask and shift to determine number of operands
            num_operands = (ir & 0b11000000) >> 6
            alu_handle = (ir & 0b00100000) >> 5

            if alu_handle:
                self.alu(ir, operand_a, operand_b)

            if ir == LDI:
                """LDI opcode, store value at specified spot in register"""
                self.reg[operand_a] = operand_b
            elif ir == PRN:
                print(self.reg[operand_a])
            elif ir == HLT:
                print('Code halting...')
                """ HLT opcode, stop loop"""
                running = False
                break
            # elif ir == MUL:
            #     self.alu("MUL", operand_a, operand_b)

            self.pc += num_operands + 1
