"""
    Cat Interactive mode.

    (repl - Read, Evaluate, Print, Loop)
"""

import sys
import traceback
import readline

MOTD = (
    "words -- prints a list of built-in Cat words (functions)",
    "'wordName doc -- prints documentation for wordName",
    "'wordName def -- prints the definition of wordName",
    "To run a series of tests use the word 'runtests'",
    "'quit' or ^D exits the interpreter",
    "\\ continues input onto a new line with prompt '...>'",
)

MOTD_COLOR = 'green'


class REPL:

    def __init__(self, cat):
        self.cat = cat
        self._show_stack = True
        self._full_error_info = 'off'

    def print_motd(self):
        for line in MOTD:
            self.cat.output(line, MOTD_COLOR)

    def run(self):
        self.print_motd()

        while True:
            self.cat.eval('global:prompt')  # because user may have changed the prompt
            prompt = self.cat.pop()         # Pop is the value of global:prompt
            line   = ''
            
            while( True ) :
                try:
                    line += raw_input( prompt )
                
                except EOFError:
                    # CTRL+D
                    line = 'quit'
                    break
                
                if line.endswith("\\") :
                    prompt = "...> "
                    line = line[:-1]
                
                else :
                    break

            if line in ('quit'):
                # Newline between empty cat prompt and command line prompt.
                self.cat.output('')
                break

            elif line.lower().startswith("showstack"):
                self._show_stack = line.lower().endswith(('on', 'true', 'yes'))

            elif line.lower().startswith("fullerrorinfo"):
                if line.lower().endswith(('on', 'true', 'yes')) :
                    self._full_error_info = 'on'
                
                elif line.lower().endswith( 'super' ) :
                    self._full_error_info = 'super'
                
                else :
                    self._full_error_info = 'off'

            else :
                try:
                    self.cat.eval(line.strip())
    
                    if self._show_stack:
                        self.cat.output(str(self.cat), 'blue')
    
                except Exception, msg:
                    # For now, I'd rather see exceptions rather than hide them
                    self.cat.output(str(msg), 'red')
                    self.cat.output(str(self.cat), 'blue')
                    
                    if self._full_error_info == 'super' :
                        raise
                    
                    elif self._full_error_info == 'on':
                        for frame in traceback.extract_tb(sys.exc_info()[2]):
                            _, lineno, fn, _ = frame
                            self.cat.output("Error in %s on line %d" % (fn, lineno), 'red')
