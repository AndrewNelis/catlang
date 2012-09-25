"""
    Cat Interactive mode.

    (repl - Read, Evaluate, Print, Loop)
"""

import sys
import traceback
import readline
from termcolor import colored

MOTD = (
    "all_words     -- prints a list of built-in Cat words (functions)",
    "'wordName doc -- prints documentation for wordName",
    "'wordName def -- prints the definition of wordName",
    "'name help    -- prints documentation for words, modules, classes, etc",
    "To run a series of tests use the word 'runtests'",
    "'quit' or ^D exits the interpreter",
    "\\ continues input onto a new line with prompt '...>'",
)

MOTD_COLOR = 'green'


class REPL:

    def __init__(self, cat):
        self.cat              = cat
        self._show_stack      = cat.ns.config.getboolean( 'stack', 'show_stack' )
        self._full_error_info = cat.ns.config.get( 'errors', 'full_error_info' )

    def print_motd(self):
        for line in MOTD:
            self.cat.output(line, MOTD_COLOR)

    def run(self):
        self.print_motd()

        # set up display colours
        if self.cat.ns.config.getboolean( 'display', 'use_colour' ) :
            e_c = self.cat.ns.config.get( 'display', 'error' )
            p_c = self.cat.ns.config.get( 'display', 'prompt' )
            s_c = self.cat.ns.config.get( 'display', 'stack' )
        
        else :
            e_c = None
            p_c = None
            s_c = None

        # load initialization file if any
        fileName = self.cat.ns.config.get( 'paths', 'load_file' )
        
        if fileName :
            self.cat.eval( "'" + fileName + " load" )
        
        # main interactive loop
        while True:
            self.cat.eval('global:prompt')  # because user may have changed the prompt
            prompt = colored( "\n" + self.cat.pop() + " ", p_c )  # Pop is the value of global:prompt
            line   = ''
            
            # loop so multi-line input can be collected
            while( True ) :
                try:
                    line += raw_input( prompt )
                
                except EOFError:
                    # CTRL+D
                    line = 'quit'
                    break
                
                if line.endswith("\\") :
                    prompt = colored( "...> ", p_c )
                    line   = line[:-1]
                
                else :
                    break

            if line == 'quit':
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
                        self.cat.output( str(self.cat), s_c )
    
                except Exception, msg:
                    # For now, I'd rather see exceptions rather than hide them
                    self.cat.output(str(msg), e_c)
                    self.cat.output(str(self.cat), s_c)
                    
                    if self._full_error_info == 'super' :
                        raise
                    
                    elif self._full_error_info == 'on':
                        for frame in traceback.extract_tb(sys.exc_info()[2]):
                            _, lineno, fn, _ = frame
                            self.cat.output("Error in %s on line %d" % (fn, lineno), e_c)
