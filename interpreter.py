import re

from reg_names import REG_NAMES
from encode import encode

class Interpreter:
    def __init__(self,
                 PROG_START=0x1000):
        """
        Create new Interpreter. Params:
            - PROG_START: location in memory where instructions live
        """
        # Core components
        self.pc = PROG_START
        self.reg = [0] * 4
        self.mem = [0] * (1<<16)
        self.labels = {}

        # Config params
        self.PROG_START = PROG_START

    def dump_state(self):
        """
        Print state.
        """
        print(f"PC={self.pc}")
        print(f"Regs: ", end="")
        for i in range(4):
            print(f"{REG_NAMES[i][0]}={hex(self.reg[i])}")
    
    def load_prog(self, prog: str):
        """
        STRING PARSING !!
        Loads a program into memory at address self.PROG_START.
        First pass:
            - Convert pseudoinstructions to real instructions
            - Get locations of labels
        """
        lines = prog.strip().split("\n")
        insts = []

        # FIRST PASS: convert pseudoinstructions, get label locations
        cur_addr = self.PROG_START
        for line_no, line in enumerate(lines):
            line = line.split("#", 1)[0].strip()
            if len(line) == 0:
                continue
            
            # Line contains single label, e.g. "loop:"
            pure_label_match = re.findall(r"^(\w+):$", line)
            if pure_label_match:
                label = pure_label_match[0]
                self.labels[label] = cur_addr
            
            else:
                # Line is of the form [label:] opcode arg1, arg2[, arg3]
                inst_match = re.findall(r"(?:(\w+):)?\s*(.+)", line)[0]
                label, inst = inst_match
                if label != "":
                    self.labels[label] = cur_addr
                
                insts.append((line_no, cur_addr, inst))

            # Increment cur address by instruction width
            # TODO: change once we have pseudoinstructions
            cur_addr += 2

        # SECOND PASS: write instructions to memory, etc.
        cur_addr = self.PROG_START
        for line_no, addr, inst in insts:
            try:
                print(f"=== {line_no}: {inst} ===")
                encoding = encode(inst, addr, self.labels)
                print(bin(encoding)[2:].zfill(16))
            except Exception as e:
                print(f"Error at line {line_no+1}: {e}")
                exit(1)


if __name__ == "__main__":
    with open("./scripts/test.S") as fin:
        prog = fin.read()
    
    interp = Interpreter()
    interp.load_prog(prog)
