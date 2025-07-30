#Only this file is allowed to output
import copy
import os
from KUtils import FileUtils as fu, ListUtils as liu
from KUtils.Typing import *

class BreakingCodeViolation(Exception): pass

BEGIN_STR = '### KUtils CodeWriter Injection Point Starts'
END_STR = '### KUtils CodeWriter Injection Point Ends'

class CodeInjector:
    def __init__(self, lines, graceful_exit:bool= False):
        self.graceful = graceful_exit
        self.begin_i = -1
        self.end_i = -1
        self.orig_lines = None
        cando = self.parse_injectable(lines)
        self._buffer: List[str] = []

    def __enter__(self)->Self:
        return self
    def parse_injectable(self, lines: str)->bool:
        begin_i = -1
        endi = -1
        for i, line in enumerate(lines):
            if BEGIN_STR in line:
                begin_i = i
            if END_STR in line:
                end_i = i

        if end_i > begin_i and begin_i > 0:
            self.begin_i, self.end_i = begin_i, end_i
            self.orig_lines = lines
        else:
            if self.graceful:
                return False
            else:
                raise BreakingCodeViolation(f'Cannot find injection point, tearing down. {begin_i, end_i}')

    def write_line(self, line: str)->None:
        self._buffer.append(line)

    def write_lines(self, lines: List[str])->None:
        self._buffer += lines

    def pop(self)->List[str]:
        ret = self.orig_lines[0:self.begin_i+1] + self._buffer + self.orig_lines[self.end_i:]
        return ret

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self
        pass

class CodeWriter:
    def __init__(self, filepath: str):
        if not filepath.endswith('Playground.py'):
            raise BreakingCodeViolation(f'You SHALL NOT WRITE TO {filepath}')

        self.read_buffer = open(filepath, 'r').readlines()
        self._write_buffer = []
        self._filepath = filepath

    def dummy_inject(self, patch: str, out_path: str = None)->None:
        out_path = out_path or self._filepath.replace('.py', '.generated.py')
        patch = liu.force_list(patch)

        with CodeInjector(self.read_buffer) as injector:
            injector.write_lines(patch)
            self._write_buffer = injector.pop()
        self.__writes(out_path)

    def __writes(self, outpath: str)->None:
        with open(outpath, 'w') as outfile:
            outfile.writelines(self._write_buffer)