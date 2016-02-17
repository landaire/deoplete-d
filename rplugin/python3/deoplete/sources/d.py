import os
import re
import subprocess
import sys

from .base import Base

from deoplete.util import charpos2bytepos
from deoplete.util import error

current_dir = os.path.dirname(os.path.abspath(__file__))
ujson_dir = os.path.dirname(current_dir)
sys.path.insert(0, ujson_dir)


class Source(Base):
    def __init__(self, vim):
        Base.__init__(self, vim)

        self.name = 'd'
        self.mark = '[d]'
        self.filetypes = ['d']
        self.input_pattern = r'(?:\b[^\W\d]\w*|[\]\)])\.(?:[^\W\d]\w*)?'
        self.rank = 500
        self.class_dict = {
            'c': 'class', # - class name
            'i': 'interface', # - interface name
            's': 'struct', # - struct name
            'u': 'union', # - union name
            'v': 'var', # - variable name
            'm': 'var', # - member variable name
            'k': 'keyword', # - keyword, built-in version, scope statement
            'f': 'function', # - function or method
            'g': 'enum', # - enum name
            'e': 'enum', # - enum member
            'P': 'package', # - package name
            'M': 'module', # - module name
            'a': 'array', # - array
            'A': 'aarray', # - associative array
            'l': 'alias', # - alias name
            't': 'template', # - template name
            'T': 'mixin template', # - mixin template name
        }

        self._dcd_client_binary = self.vim.vars['deoplete#sources#d#dcd_client_binary']
        self._dcd_server_binary = self.vim.vars['deoplete#sources#d#dcd_server_binary']
        if self.vim.vars['deoplete#sources#d#dcd_server_autostart'] == 1:
            process = subprocess.Popen([self.dcd_server_binary()], start_new_session=True)

    def get_complete_position(self, context):
        m = re.search(r'\w*$', context['input'])
        return m.start() if m else -1

    def gather_candidates(self, context):
        line = self.vim.current.window.cursor[0]
        column = context['complete_position']

        buf = self.vim.current.buffer
        offset = self.vim.call('line2byte', line) + \
            charpos2bytepos(self.vim, context['input'][: column], column) - 1
        source = '\n'.join(buf).encode()

        process = subprocess.Popen([self.dcd_client_binary(),
                                    '-c' + str(offset),
                                    buf.name,],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   start_new_session=True)
        process.stdin.write(source)
        stdout_data, stderr_data = process.communicate()
        result = stdout_data.decode().split('\n')

        if result[0] == "identifiers":
            return self.identifiers_from_result(result)
        elif result[0] ==  "calltips":
            return self.calltips_from_result(result)

        return []

    def identifiers_from_result(self, result):
        out = []
        sep = ' '

        candidates = []
        longest_class_length = 0
        for complete in result[1:]:
            if complete.strip() == '':
                continue

            pieces = complete.split("\t")
            if len(pieces) < 2:
                raise Exception(pieces)

            candidates.append(pieces)

            class_len = len(self.class_dict[pieces[1]])

            if class_len > longest_class_length:
                longest_class_length = class_len

        for pieces in candidates:
            word = pieces[0]
            _class = self.class_dict[pieces[1]]
            abbr = _class.ljust(longest_class_length + 1) + word
            info = _class

            candidate = dict(word=word,
                              abbr=abbr,
                              info=info,
                              dup=1
                              )

            out.append(candidate)

        return out

    def calltips_from_result(self, result):
        out = []

        result = result[1]

        word = result.split(" ")
        word = word[1]
        word = word[:word.find('(')]

        out.append(dict(
                word=word,
                info=result
            ))

        return out

    def dcd_client_binary(self):
        try:
            if os.path.isfile(self._dcd_client_binary):
                return self._dcd_client_binary
            else:
                raise
        except Exception:
            return self.find_binary_path('dcd-client')

    def dcd_server_binary(self):
        try:
            if os.path.isfile(self._dcd_server_binary):
                return self._dcd_server_binary
            else:
                raise
        except Exception:
            return self.find_binary_path('dcd-server')

    def find_binary_path(self, cmd):
        def is_exec(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        fpath, fname = os.path.split(cmd)
        if fpath:
            if is_exec(cmd):
                return cmd
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                binary = os.path.join(path, cmd)
                if is_exec(binary):
                    return binary
        return error(self.vim, cmd + ' binary not found')

