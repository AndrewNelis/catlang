"""
    Cat Interactive mode.

    (repl - Read, Evaluate, Print, Loop)
"""

import sys
import traceback

MOTD = (
    "#words prints a list of built-in Cat words (functions)",
    "'wordName #doc prints documentation for wordName",
    "'wordName #def prints the definition of wordName",
    "A 'naked' CR terminates interactive session as does the word 'quit'",
    "The word 'runtests' runs some test code",
)

MOTD_COLOR = 'green'


class REPL:

    def __init__(self, cat):
        self.cat = cat
        self._show_stack = True
        self._full_error_info = False

    def print_motd(self):
        for line in MOTD:
            self.cat.output(line, MOTD_COLOR)

    def run(self):
        self.print_motd()

        show_stack = False
        full_error_info = False

        while True:
            self.cat.eval('global:prompt')

            try:
                # Pop is the value of global:prompt
                line = raw_input(self.cat.pop())
            except EOFError:
                # CTRL+D
                line = 'quit'

            if line in ('', 'quit'):
                # Newline between empty cat prompt and command line prompt.
                self.cat.output('')
                break

            elif line.lower().startswith("showstack"):
                show_stack = line.lower().endswith(('on', 'true', 'yes'))

            elif line.lower().startswith("fullerrorinfo"):
                full_error_info = line.lower().endswith(('on', 'true', 'yes'))

            try:
                self.cat.eval(line.strip())

                if show_stack:
                    self.cat.output(str(self.cat), 'blue')

            except Exception, msg:
                # For now, I'd rather see exceptions rather than hide them
                raise
                self.cat.output(msg, 'red')

                if full_error_info:
                    for frame in traceback.extract_tb(sys.exc_info()[2]):
                        _, lineno, fn, _ = frame
                        self.cat.output("Error in %s on line %d" % (fn, lineno), 'red')

                self.cat.output(str(self.cat), 'blue')
