from collections import defaultdict
from typing import Set, DefaultDict, Dict

import capstone as cs

from util import dsym, elf, utils


class FunctionChecker:
    def __init__(self):
        self.md = cs.Cs(cs.CS_ARCH_ARM64, cs.CS_MODE_ARM)
        self.md.detail = True
        self.my_symtab = elf.build_name_to_symbol_table(elf.my_symtab)
        self.dsymtab = dsym.DataSymbolContainer()
        self.decompiled_fns: Dict[int, str] = dict()
        self.load_data_for_project()

    def get_data_symtab(self) -> dsym.DataSymbolContainer:
        return self.dsymtab

    def load_data_for_project(self) -> None:
        self.decompiled_fns = {func.addr: func.decomp_name for func in utils.get_functions() if func.decomp_name}
        self.get_data_symtab().load_from_csv(utils.get_repo_root() / "data" / "data_symbols.csv")

    def check(self, base_fn: elf.Function, my_fn: elf.Function) -> bool:
        gprs1: DefaultDict[int, int] = defaultdict(int)
        gprs2: DefaultDict[int, int] = defaultdict(int)
        adrp_pair_registers: Set[int] = set()

        size = len(base_fn)
        if len(base_fn) != len(my_fn):
            return False

        for i1, i2 in zip(self.md.disasm(base_fn.data, base_fn.addr), self.md.disasm(my_fn.data, my_fn.addr)):
            if i1.bytes == i2.bytes:
                if i1.mnemonic == 'adrp':
                    gprs1[i1.operands[0].reg] = i1.operands[1].imm
                    gprs2[i2.operands[0].reg] = i2.operands[1].imm
                    adrp_pair_registers.add(i1.operands[0].reg)
                elif i1.mnemonic == 'ldr':
                    reg = i1.operands[1].value.mem.base
                    if reg in adrp_pair_registers:
                        adrp_pair_registers.remove(reg)
                elif i1.mnemonic == 'ldp':
                    reg = i1.operands[2].value.mem.base
                    if reg in adrp_pair_registers:
                        adrp_pair_registers.remove(reg)
                elif i1.mnemonic == 'add':
                    reg = i1.operands[1].reg
                    if reg in adrp_pair_registers:
                        adrp_pair_registers.remove(reg)
                continue

            if i1.mnemonic != i2.mnemonic:
                return False

            # Ignore some address differences until a fully matching executable can be generated.

            if i1.mnemonic == 'bl':
                if not self._check_function_call(i1.operands[0].imm, i2.operands[0].imm):
                    return False
                continue

            if i1.mnemonic == 'b':
                branch_target = i1.operands[0].imm
                # If we are branching outside the function, this is likely a tail call.
                # Treat this as a function call.
                if not (base_fn.addr <= branch_target < base_fn.addr + size):
                    if not self._check_function_call(branch_target, i2.operands[0].imm):
                        return False
                    continue
                # Otherwise, it's a mismatch.
                return False

            if i1.mnemonic == 'adrp':
                if i1.operands[0].reg != i2.operands[0].reg:
                    return False
                reg = i1.operands[0].reg

                gprs1[reg] = i1.operands[1].imm
                gprs2[reg] = i2.operands[1].imm

                adrp_pair_registers.add(reg)
                continue

            if i1.mnemonic == 'ldr' or i1.mnemonic == 'str':
                if i1.operands[0].reg != i2.operands[0].reg:
                    return False
                if i1.operands[1].value.mem.base != i2.operands[1].value.mem.base:
                    return False
                reg = i1.operands[1].value.mem.base
                if reg not in adrp_pair_registers:
                    return False

                gprs1[reg] += i1.operands[1].value.mem.disp
                gprs2[reg] += i2.operands[1].value.mem.disp
                if not self._check_data_symbol(gprs1[reg], gprs2[reg]):
                    return False

                adrp_pair_registers.remove(reg)
                continue

            if i1.mnemonic == 'ldp' or i1.mnemonic == 'stp':
                if i1.operands[0].reg != i2.operands[0].reg:
                    return False
                if i1.operands[1].reg != i2.operands[1].reg:
                    return False
                if i1.operands[2].value.mem.base != i2.operands[2].value.mem.base:
                    return False
                reg = i1.operands[2].value.mem.base
                if reg not in adrp_pair_registers:
                    return False

                gprs1[reg] += i1.operands[1].value.mem.disp
                gprs2[reg] += i2.operands[1].value.mem.disp
                if not self._check_data_symbol(gprs1[reg], gprs2[reg]):
                    return False

                adrp_pair_registers.remove(reg)
                continue

            if i1.mnemonic == 'add':
                if i1.operands[0].reg != i2.operands[0].reg:
                    return False
                if i1.operands[1].reg != i2.operands[1].reg:
                    return False
                reg = i1.operands[1].reg
                if reg not in adrp_pair_registers:
                    return False

                gprs1[reg] += i1.operands[2].imm
                gprs2[reg] += i2.operands[2].imm
                if not self._check_data_symbol(gprs1[reg], gprs2[reg]):
                    return False

                adrp_pair_registers.remove(reg)
                continue

            return False

        return True

    def _check_data_symbol(self, orig_addr: int, decomp_addr: int) -> bool:
        symbol = self.dsymtab.get_symbol(orig_addr)
        if symbol is None:
            return True

        decomp_symbol = self.my_symtab[symbol.name]
        return decomp_symbol.addr == decomp_addr

    def _check_function_call(self, orig_addr: int, decomp_addr: int) -> bool:
        name = self.decompiled_fns.get(orig_addr, None)
        if name is None:
            return True

        decomp_symbol = self.my_symtab[name]
        return decomp_symbol.addr == decomp_addr
