"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 7
        self.pc = 0
        self.commands = {
            0b00000001: self.hlt,
            0b10000010: self.ldi,
            0b01000111: self.prn,
            0b10100010: self.mul
        }
        self.opcodes = {
            "NOP":  0b00000000,
            "LDI":  0b10000010,
            "PRN":  0b01000111,
            "ADD":  0b10100000,
            "MUL":  0b10100010,
            "HLT":  0b00000001,
            "PUSH": 0b01000101,
            "POP":  0b01000110,
            "CALL": 0b01010000,
            "RET":  0b00010001,
            "CMP":  0b10100111,
            "JMP":  0b01010100,
            "JEQ":  0b01010101,
            "JNE":  0b01010110,
        }

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def hlt(self, operand_a, operand_b):
        return (0, False)

    def ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b
        return (3, True)

    def prn(self, operand_a, operand_b):
        print(self.reg[operand_a])
        return (2, True)

    def mul(self, operand_a, operand_b):
        self.alu("MUL", operand_a, operand_b)
        return (3, True)

    def push(self):
        """Run push onto the stack."""
        # grab the target reg idx
        reg_idx = self.ram[self.pc+1]
        # grab the value to be pushed from the reg idx
        push_val = self.reg[reg_idx]
        # grab the stack pointer
        sp = self.reg[7]
        # push the value onto the stack
        self.ram[sp] = push_val
        # decremment the sp by 1
        self.reg[7] -= 1

    def pop(self):
        """Run pop off the stack."""
        # grab the target reg idx
        reg_idx = self.ram[self.pc+1]
        # return the sp to the last value in stack
        self.reg[7] += 1
        # grab the new stack pointer
        sp = self.reg[7]
        # grab the value to be popped from the stack
        pop_val = self.ram[sp]
        # set the last stack value to 0
        self.ram[sp] = 0
        # add the popped value to the reg idx
        self.reg[reg_idx] = pop_val

    def load(self, program):
        """Load a program into memory."""

        address = 0

        with open(program) as f:
            for line in f:
                comment_split = line.split('#')
                number = comment_split[0].strip()

                try:
                    self.ram_write(int(number, 2), address)
                    address += 1
                except ValueError:
                    pass

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] = (self.reg[reg_a] * self.reg[reg_b])
        # if op == "INC":
        #     self.reg[reg_a] += 1
        # elif op == "DEC":
        #     self.reg[reg_a] -= 1
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
        running = True

        while running:
            ir = self.ram[self.pc]

            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            try:
                operation_output = self.commands[ir](operand_a, operand_b)
                running = operation_output[1]
                self.pc += operation_output[0]

            except:
                print(f"Unknown command: {ir}")
                sys.exit()
