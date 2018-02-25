# =============================================================================
# FILE: clangx.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# =============================================================================

import re
import os.path
import subprocess
import shlex
from itertools import chain

from deoplete.util import getlines, error
from .base import Base


class Source(Base):
    def __init__(self, vim):
        Base.__init__(self, vim)

        self.name = 'clangx'
        self.filetypes = ['c', 'cpp']
        self.mark = '[clangx]'
        self.rank = 500
        self.executable_clang = self.vim.call('executable', 'clang')
        self.encoding = self.vim.eval('&encoding')
        self.input_pattern = r'\.[a-zA-Z0-9_?!]*|[a-zA-Z]\w*::\w*|->\w*'

    def get_complete_position(self, context):
        m = re.search('[a-zA-Z0-9_]*$', context['input'])
        return m.start() if m else -1

    def gather_candidates(self, context):
        if not self.executable_clang:
            return []

        line = context['position'][1]
        column = context['complete_position']
        lang = 'c++' if context['filetype'] == 'cpp' else 'c'
        buf = '\n'.join(getlines(self.vim)).encode(self.encoding)

        args = [
            'clang', '-x', lang, '-fsyntax-only',
            '-Xclang', '-code-completion-macros',
            '-Xclang', '-code-completion-at=-:{}:{}'.format(line, column),
            '-',
            '-I', os.path.dirname(context['bufpath']),
        ]
        args += self._args_from_neoinclude(context)
        args += self._args_from_clang(context, '.clang')
        args += self._args_from_clang(context, '.clang_complete')

        try:
            proc = subprocess.Popen(args=args,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.DEVNULL,
                                    cwd=context['cwd'])
            result, errs = proc.communicate(buf, timeout=10)
            result = result.decode(self.encoding)
        except subprocess.TimeoutExpired as e:
            proc.kill()
            return []

        return self._parse_lines(result.splitlines())

    def _args_from_neoinclude(self, context):
        if not self.vim.call(
                'exists', '*neoinclude#get_path'):
            return []

        return list(chain.from_iterable(
            [['-I', x] for x in
             self.vim.call('neoinclude#get_path',
                           context['bufnr'],
                           context['filetype']).replace(';', ',').split(',')
             if x != '']))

    def _args_from_clang(self, context, name):
        clang_file = self.vim.call('findfile', name, '.;')
        if not clang_file:
            return []

        try:
            with open(clang_file) as f:
                return shlex.split(' '.join(f.readlines()))
        except Exception as e:
            error(self.vim, 'Parse Failed: ' + clang_file)
        return []

    def _parse_lines(self, lines):
        candidates = []
        for line in lines:
            m = re.search('^COMPLETION:\s+(.{,}?) : (.{,}?)$', line)
            if not m:
                m = re.search('^COMPLETION:\s+(.*)$', line)
                if m:
                    candidates.append({'word': m.group(1)})
                continue

            menu = m.group(2)
            menu = menu.replace('[#', '')
            menu = menu.replace('#]', '')
            menu = menu.replace('<#', '')
            menu = menu.replace('#>', '')
            menu = menu.replace('{#', '')
            menu = menu.replace('#}', '')

            word = m.group(1)
            if word.startswith('PFNG'):
                continue

            candidate = {'word': word, 'dup': 1}
            if menu != word:
                candidate['menu'] = menu
            candidates.append(candidate)
        return candidates
