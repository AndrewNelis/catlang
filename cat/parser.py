"""
    Parser.

    This only parses supplied text, it does not alter the stack.
"""


from collections import namedtuple
import re

Definition = namedtuple('Definition', ['name', 'effect', 'description', 'definition', 'dependencies'])


class Parser:

    def __init__(self):
        self.parseInt = re.compile(r'^0\((?P<base>\d+)\)(?P<value>.*)$')
        self.parseModule = re.compile(r'(\w+)([.]\w+)+')
        self.parseDef = re.compile(r'''
                    define\s+
                    (?P<name>\S+)\s*
                    (?P<effect>:\s*\(.*\))?\s*
                    (?P<desc>\{\{.*\}\})?\s*
                    {(?P<definition>[^}]*)}''', re.DOTALL | re.VERBOSE)
        self.findDeps = re.compile(r'deps:\s*(\S+)')

    def collect_function(self, line, dopen='[', dclose=']'):
        '''
        returns the string enclosed between the open and close delimiters

        :param line: the string to be analyzed
        :type line: string
        :param dopen: the opening delimiter
        :type dopen: string
        :param close: the closing delimiter
        :type close: string
        :rtype: string

        >>> p = Parser()
        >>> p.collect_function('[1 2 3] a b c')
        ('[1 2 3]', ' a b c')

        >>> p.collect_function('[ test [ 1 2 3] ] a')
        ('[ test [ 1 2 3] ]', ' a')
        '''

        buf = ""
        count = 0

        while line:
            c = line[0]
            buf += c

            if c == dopen:
                count += 1

            elif c == dclose:
                count -= 1

                if count == 0:
                    return buf, line[1:]

            line = line[1:]

        return buf, line.lstrip()

    def intern(self, value):
        '''
        Convert string representation of a number or word to its internal form
        Numbers MUST start with a digit (or +/-, as long as the remainder are numbers)
        If the value is not a number it is returned as is
        Floating point numbers MUST have a decimal point
        Integers may be of the form (where 'd' is a decimal digit, h a hex  digit)
            dddd -- decimal integer
            0xhhhh -- hex integer
            0dddd -- octal integer
            0bdddd -- binary integer
            0(z)xxxx -- integer to base z (for bases > 10, digits following 9 are a,b,c,d,...,y,z)

            >>> p = Parser()
            >>> p.intern('12')
            12
            >>> p.intern('0x11')
            17
            >>> p.intern('022')
            18
            >>> p.intern('0b10101')
            21
            >>> p.intern('0(12)123')
            171
            >>> p.intern('-109')
            -109
            >>> p.intern('+109')
            109
            >>> p.intern('NaN')
            'NaN'
            >>> p.intern('1e4')
            10000.0
            >>> p.intern('2E3')
            2000.0
            >>> p.intern('12.5')
            12.5
            >>> p.intern('++')
            '++'
            >>> p.intern('--')
            '--'
        '''
        if len(value) == 0:
            return value

        if len(value) == 1:
            if value.isdigit():
                return int(value)
            else:
                return value

        sign = +1

        if value[1].isdigit():
            # Second char has to be a digit, otherwise we might be doing
            # something e.g. to '--', not '+1'
            if value.startswith('-'):
                sign = -1
                value = value[1:]

            elif value.startswith('+'):
                sign = +1
                value = value[1:]

        if value[0].isdigit():

            base = 10

            # have a number
            if value.count(".") == 1 or value.lower().count("e") == 1:
                # have a float
                return sign * float(value)

            # have an integer
            if value.startswith('0b'):
                base = 2

            elif value.lower().startswith('0x'):
                base = 16

            elif value.startswith("0("):
                mo = self.parseInt.match(value)

                if mo is None:
                    return value

                base = int(mo.group('base'))
                value = mo.group('value')

            elif value.startswith('0'):
                base = 8

            return sign * int(value, base)

        else:
            # have something else
            return value

    def _consume_to(self, line, ending, include_end):
        """
            Parser helper. Consume and return line up to the first <ending>

            First char in <line> is assumed to be the opener and doesn't count
            as an ending

            >>> p = Parser()
            >>> p._consume_to('"test" something else', '"', True)
            ('"test"', ' something else')
            >>> p._consume_to("'constant 1 2 3", ' ', False)
            ("'constant", ' 1 2 3')
            >>> p._consume_to("1 ++", ' ', False)
            ('1', ' ++')
            >>> p._consume_to("++", ' ', False)
            ('++', '')
        """

        index = line.find(ending, 1)

        if index > 0:
            return line[:index + include_end], line[index + include_end:]
        else:
            # Unmatched ending.
            return line, ''

    def gobble(self, expr):
        """Return the given expression a token at a time allowing for string
        quoting and anonymous functions

        >>> p = Parser()
        >>> list(p.gobble('test'))
        ['test']
        >>> list(p.gobble('1 2 3'))
        [1, 2, 3]
        >>> list(p.gobble('1 [ 2 3 [4] ] 5'))
        [1, [2, 3, [4]], 5]
        >>> list(p.gobble("1 'test"))
        [1, '"test"']
        >>> list(p.gobble('"a" "b" "c"'))
        ['"a"', '"b"', '"c"']
        >>> list(p.gobble('0x10 0b1100'))
        [16, 12]
        >>> list(p.gobble("'test 'test2 1 2 3"))
        ['"test"', '"test2"', 1, 2, 3]
        >>> list(p.gobble('"Strings can have spaces and \\' in them" \\'sentinel 1'))
        ['"Strings can have spaces and \\' in them"', '"sentinel"', 1]
        >>> list(p.gobble('1 ++'))
        [1, '++']
        >>> list(p.gobble('clear 1 ++ 2 --'))
        ['clear', 1, '++', 2, '--']
        """

        while expr:
            char = expr[0]

            if char in "\t\r\n ":
                expr = expr[1:]
                continue

            if char == '[':
                function, expr = self.collect_function(expr)
                yield list(self.gobble(function[1:-1]))

            elif char == '"':
                string, expr = self._consume_to(expr, '"', True)
                yield string

            elif char == "'":
                string, expr = self._consume_to(expr, ' ', False)
                yield '"%s"' % string[1:]

            else:
                string, expr = self._consume_to(expr, ' ', False)
                # intern will try and find something that looks like a
                # number. Otherwise it's returned wholesale.
                yield self.intern(string)

    def parse_definition(self, line):
        """
            Parse the line containing a function definition.

            Return a Definition namedtuple object.

            >>> p = Parser()
            >>> d = p.parse_definition('define test { 1 2 + }')
            >>> d.name
            'test'
            >>> d.definition
            '1 2 +'

            >>> p.parse_definition('define nothing')
            Traceback (most recent call last):
                ...
            Exception: expect functions of the form "define name (: effect)? {{description}}? {definition}"

            >>> d = p.parse_definition('define test2 : ( -- ) {{ This is test 2 }} { }')
            >>> d.effect
            ': ( -- )'
            >>> d.description
            'This is test 2'

            >>> d = p.parse_definition('define test2 {{ deps: foo,bar }} {}')
            >>> d.dependencies
            ['foo', 'bar']

        """
        match = self.parseDef.match(line)

        if match is None:
            raise Exception('expect functions of the form "define name (: effect)? {{description}}? {definition}"')

        name, effect, description, definition = match.groups()

        if description:
            description = description.strip('{} ')
        else:
            description = ' none'

        if not effect:
            effect = ' : none'

        if definition:
            definition = definition.strip()

        # look for dependencies (e.g. for word abba we would have deps:abab,aba or just deps:abab as abab has deps:aba)
        match_depends = self.findDeps.finditer(description)

        dependencies = []

        if match_depends is not None:
            for depend in match_depends:
                words = depend.group(1)
                dependencies.extend([w for w in words.split(',') if w])

        return Definition(
            name,
            effect,
            description,
            definition,
            dependencies,
        )
