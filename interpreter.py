import re
import sys
from pprint import pprint

from encode import encode
from execute import execute

from decode import decode
from utils.reg_names import REG_NAMES, VREG_NAMES

class Interpreter:
    def __init__(self,
                 PROG_START=0x1000):
        """
        Create new Interpreter. Params:
            - PROG_START: location in memory where instructions live
        """
        # Core components
        self.pc = PROG_START
        self.reg = [0, 0, 0, 0, 0]
        self.mem = [0] * (1<<16)
        self.labels = {}

        # Config params
        self.PROG_START = PROG_START

    def dump_state(self):
        """
        Print state.
        """
        print(f"pc: {self.pc:>4}\tinst: 0b{bin(self.mem[self.pc])[2:].zfill(16)}", end=" ")
        print(f"{decode(self.mem[self.pc]):>20}", end="\t")

        MODE = "decimal"
        if MODE == "decimal":
            print("regs:", ", ".join([f"{str(x).rjust(6)}" for x in self.reg]))
        elif MODE == "hex":
            print("regs:", ", ".join([f"0x{hex(x)[2:].zfill(8)}" for x in self.reg]))

    def dump_program(self):
        """
        Print contents of program.
        """
        cur_addr = self.PROG_START
        while self.mem[cur_addr] > 0:
            print(hex(cur_addr), "\t", bin(self.mem[cur_addr])[2:].zfill(16), "\t", decode(self.mem[cur_addr]))
            cur_addr += 1
    
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
            self.dump_state()
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

        # Opcodes and register names are illegal labels
        def is_valid_label(label: str) -> bool:
            opcodes = ["addi", "nandi",
                       "swb", "sl", "sr", "nand", "add",
                       "jalr",
                       "bn", "bz", "bp",
                       "lw", "sw",
                       "jal", "halt", "nop", "li"]
            if label in opcodes:
                return False
            for names in REG_NAMES + VREG_NAMES:
                if names != None and label in names:
                    return False
            return re.match(r"^[\w\d_]+$", label) is not None

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
                if not is_valid_label(label):
                    raise NameError(f"Label '{label}' is not valid")
                self.labels[label] = cur_addr
            
            else:
                # Line is of the form [label:] opcode arg1, arg2[, arg3]
                inst_match = re.findall(r"(?:(\w+):)?\s*(.+)", line)[0]
                label, inst = inst_match
                if label != "":
                    if not is_valid_label(label):
                        raise NameError(f"Label '{label}' is not valid")
                    self.labels[label] = cur_addr
                
                # Update list of instructions
                # Line number is tracked for error handling
                insts.append((line_no, cur_addr, inst))

                # Some pseudoinstructions are multiple words.
                # This is inefficient but makes for more concise code!
                try:
                    inst_width = len(encode(inst, cur_addr, None))
                except Exception as e:
                    print(f"Error loading instruction '{inst}': {e}")
                    raise e
                    exit(1)
                    
                cur_addr += inst_width

        # SECOND PASS: write instructions to memory, etc.
        cur_addr = self.PROG_START
        for line_no, addr, inst in insts:
            try:
                for encoding in encode(inst, addr, self.labels):
                    self.mem[cur_addr] = encoding
                    cur_addr += 1
            
            except Exception as e:
                print(f"Error loading at line {line_no+1}: {inst}\n\t{e}")
                raise e
            
        return cur_addr - self.PROG_START


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: interpreter.py <script>")
        exit(1)

    with open(sys.argv[1]) as fin:
        prog = fin.read()
    
    interp = Interpreter()
    print(f"Loading program...")
    prog_len = interp.load_prog(prog)
    print(f"Loaded program of {prog_len} words.")
    interp.dump_program()

    interp.run()
