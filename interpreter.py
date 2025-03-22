import re

from reg_names import REG_NAMES
from encode import encode
from execute import execute

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
        print(", ".join([f"{REG_NAMES[i][0]}=0x{hex(self.reg[i])[2:].zfill(4)}" \
                         for i in range(4)]))
    
    def run(self):
        """
        Runs the program.
        """
        self.pc = self.PROG_START
        while self.pc != 0:
            self.execute_step()

        self.dump_state()
    
    def execute_step(self):
        """
        Steps the program forward.
        """
        try:
            self.pc = execute(
                self.mem[self.pc], self.reg, self.mem, self.pc)
        except Exception as e:
            print(f"Execution crashed while pc={self.pc}: {e}")
            exit(1)

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
                # print(f"\n=== {line_no}: {inst} ===")
                encoding = encode(inst, addr, self.labels)
                self.mem[cur_addr] = encoding
                cur_addr += 2
            
            except Exception as e:
                print(f"Error loading at line {line_no+1}: {e}")
                exit(1)
            
        return cur_addr - self.PROG_START


if __name__ == "__main__":
    with open("./scripts/fib.S") as fin:
        prog = fin.read()
    
    interp = Interpreter()
    print(f"Loading program...")
    prog_len = interp.load_prog(prog)
    print(f"Loaded program of {prog_len} bytes.")
    interp.run()
