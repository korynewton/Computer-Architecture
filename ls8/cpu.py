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
        # initialize where the start of stack points to in memory, store in r7
        self.sp = 0xF4
        self.reg[7] = self.ram[self.sp]

        # initialize PC that will be incremented
        self.pc = 0
        # initialize branch table with all opcodes and the functions they call
        self.branch_table = {}
        # LDI
        self.branch_table[0b10000010] = self.handle_ldi
        # PRN
        self.branch_table[0b01000111] = self.handle_prn
        # HLT
        self.branch_table[0b00000001] = self.handle_hlt
        # PUSH
        self.branch_table[0b01000101] = self.handle_push
        # POP
        self.branch_table[0b01000110] = self.handle_pop
        # RET
        self.branch_table[0b00010001] = self.handle_ret
        # CALL
        self.branch_table[0b01010000] = self.handle_call

        # JMP
        # self.branch_table[0b01010100] = self.handle_jmp

        # TODO ST, RET PRA, OR, NOT, NOP, MOD, LD, JNE, JLT, JLE, JGT, JGE, JEQ, IRET, INT,
        # INC, DEC

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
        ADD = 0b10100000
        SUB = 0b10100001
        DIV = 0b10100011
        SHL = 0b10101100
        SHR = 0b10101101
        XOR = 0b10101011

        if op == ADD:
            self.reg[reg_a] += self.reg[reg_b]
        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == SUB:
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == DIV:
            if not self.reg[reg_b]:
                print("Error: cannot divide by 0")
                sys.exit()
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == SHL:
            '''Shifts the value in rega_a left by the number of bits specified in reg_b'''
            value = self.reg[reg_a]
            shifted = value << self.reg[reg_b]
            self.reg[reg_a] = shifted
        elif op == SHR:
            '''Shifts the value in rega_a left by the number of bits specified in reg_b'''
            value = self.reg[reg_a]
            shifted = value << self.reg[reg_b]
            self.reg[reg_a] = shifted
        elif op == XOR:
            xor_res = self.reg[reg_a] ^ self.reg[reg_b]
            self.reg[reg_a] = xor_res

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

    def handle_ldi(self, operand_a, operand_b):
        # """LDI opcode, store value at specified spot in register"""
        self.reg[operand_a] = operand_b

    def handle_prn(self, operand_a):
        print(self.reg[operand_a])

    def handle_hlt(self):
        print('Code halting...')
        """ HLT opcode, stop loop"""
        sys.exit()

    def handle_push(self, operand_a):
        # decrement, then store operand in stack
        self.sp -= 1
        r_value = self.reg[operand_a]
        self.ram[self.sp] = r_value

    def handle_pop(self, operand_a):
        # store value in stack indicated by pointer, store in register at given reg index given by operand
        value = self.ram[self.sp]
        self.reg[operand_a] = value
        self.sp += 1

    # def handle_jmp(self, operand_a):
    #     self.pc = self.reg[operand_a]

    def handle_ret(self):
        '''Pop the value from the top of the stack and store it in the `PC`.'''
        ret_addr = self.ram[self.sp]
        self.pc = ret_addr
        self.sp += 1

    def handle_call(self, operand_a):
        '''Calls a subroutine (function) at the address stored in the register'''
        # push address of instructions that come after sub-routine onto stack
        self.sp -= 1
        return_addr = self.pc + 2
        self.ram[self.sp] = return_addr

        # set pc to address of subroutine start
        subr_addr = self.reg[operand_a]
        self.pc = subr_addr

    def run(self):
        """Run the CPU."""

        while True:
            # self.trace()

            # holds a copy of the currently executing 8-bit instruction
            ir = self.ram[self.pc]

            # stores operands a and b which can be 1 or 2 bytes ahead of instruction byte, or nonexistent
            operand_a = self.ram_read(self.pc+1)
            operand_b = self.ram_read(self.pc+2)

            # mask and shift to determine number of operands
            num_operands = (ir & 0b11000000) >> 6
            alu_handle = (ir & 0b00100000) >> 5

            # if CALL or RET is the opcode we'll want to increment PC differently
            if ir == 0b01010000:
                self.branch_table[ir](operand_a)
                continue
            elif ir == 0b00010001:
                self.branch_table[ir]()
                continue

            if alu_handle:
                self.alu(ir, operand_a, operand_b)

            elif num_operands == 2:
                self.branch_table[ir](operand_a, operand_b)
            elif num_operands == 1:
                self.branch_table[ir](operand_a)
            elif num_operands == 0:
                self.branch_table[ir]()
            else:
                self.handle_hlt()

            self.pc += num_operands + 1
