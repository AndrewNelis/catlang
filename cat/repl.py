"""
    Cat Interactive mode.

    (repl - Read, Evaluate, Print, Loop)
"""

import sys
import traceback
<<<<<<< HEAD

MOTD = (
    "#words prints a list of built-in Cat words (functions)",
    "'wordName #doc prints documentation for wordName",
    "'wordName #def prints the definition of wordName",
    "A 'naked' CR terminates interactive session as does the word 'quit'",
    "The word 'runtests' runs some test code",
)

MOTD_COLOR = 'green'

=======
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

>>>>>>> 07e8bdb338ec6a20356c761f0e0b188e87944d60

class REPL:

    def __init__(self, cat):
        self.cat = cat
<<<<<<< HEAD
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
=======

    def print_motd(self):
        if self.cat.ns.config.getboolean( 'misc', 'show_MOTD' ) :
            i_c = self.cat.ns.config.get( 'display', 'info' )
            
            for line in MOTD:
                self.cat.output(line, i_c)
    
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
        if self.cat.ns.config.has_option( 'paths', 'load_file' ) :
            fileName = self.cat.ns.config.get( 'paths', 'load_file' )
            
            if fileName :
                self.cat.output( "\nLoading file '%s'\n" % fileName, self.cat.ns.config.get('display', 'info') )
                self.cat.eval( "'" + fileName + " load" )
        
        # main interactive loop
        while True:
            # check for alternate stack output format (user can 'config_set' this dynamically)
            alt = self.cat.ns.config.getboolean( 'stack', 'use_alt_format' )
            
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
>>>>>>> 07e8bdb338ec6a20356c761f0e0b188e87944d60
                # Newline between empty cat prompt and command line prompt.
                self.cat.output('')
                break

<<<<<<< HEAD
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
=======
            else :
                try:
                    self.cat.eval(line.strip())
    
                    if self.cat.ns.config.getboolean( 'stack', 'show_stack' ) :  # 'config_set' can alter
                        self.cat.output( self.cat.stack.format(alt), s_c )
    
                except Exception, msg:
                    # Three response levels:
                    # super -- full backtrace and kill execution
                    # on    -- print error message with abbreviated backtrace and continue
                    # off   -- print error message and continue
                    self.cat.output(str(msg), e_c)
                    self.cat.output( self.cat.stack.format(alt), s_c )
                    fei = self.cat.ns.config.get( 'errors', 'full_error_info' )  # 'config_set' can alter
                    
                    if fei == 'super' :
                        raise
                    
                    elif fei == 'on':
                        for frame in traceback.extract_tb(sys.exc_info()[2]):
                            _, lineno, fn, _ = frame
                            self.cat.output("Error in %s on line %d" % (fn, lineno), e_c)
>>>>>>> 07e8bdb338ec6a20356c761f0e0b188e87944d60
