
import re


class CatParser:

    def __init__(self):
        self.parseInt = re.compile(r'^0\((?P<base>\d+)\)(?P<value>.*)$')
        self.parseFloat = re.compile(r'(?P<value>[+-]?\d*\.\d+([eE][+-]?\d+)?)$')
        self.parseDefine = re.compile(r'define\s*(?P<name>\S+)\s*{(?P<definition>[^}]*)}')
        self.parseModule = re.compile(r'(\w+)([.]\w+)+')
        self.parseDef = re.compile(r'define\s+(?P<name>\S+)\s*(?P<effect>:\s*\(.*\))?\s*(?P<desc>\{\{.*\}\})?\s*{(?P<definition>[^}]*)}', re.DOTALL)
        self.findDeps = re.compile(r'deps:\s*(\S+)')

    def _collectFunction(self, line, dopen='[', dclose=']'):
        '''
        returns the string enclosed between the open and close delimiters

        :param line: the string to be analyzed
        :type line: string
        :param dopen: the opening delimiter
        :type dopen: string
        :param close: the closing delimiter
        :type close: string
        :rtype: string
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

    def internNumber(self, value):
        '''
        Convert string representation of a number to its internal form
        Numbers MUST start with a digit
        If the value is not a number it is returned as is
        Floating point numbers MUST have a decimal point
        Integers may be of the form (where 'd' is a decimal digit, h a hex  digit)
            dddd -- decimal integer
            0xhhhh -- hex integer
            0dddd -- octal integer
            0bdddd -- binary integer
            0(z)xxxx -- integer to base z (for bases > 10, digits following 9 are a,b,c,d,...,y,z)
        '''
        if len(value) == 0:
            return value

        if len(value) == 1:
            if value.isdigit():
                return int(value)

            else:
                return value

        if value[0] == '-' and value[1].isdigit():
            sign = -1
            value = value[1:]

        elif value[0] == '+' and value[1].isdigit():
            sign = +1
            value = value[1:]

        else:
            sign = +1

        if value[0].isdigit():
            # have a number
            if value.count(".") == 1 or value.lower().count("e") == 1:
                # have a float
                return sign * float(value)

            else:
                # have an integer
                if value.startswith('0b'):
                    return sign * int(value, 2)

                elif value.startswith('0x') or value.startswith('0X'):
                    return sign * int(value, 16)

                elif value.startswith("0("):
                    mo = self.parseInt.match(value)

                    if mo:
                        return sign * int(mo.group('value'), int(mo.group('base')))

                    else:
                        return value

                elif value.startswith('0'):
                    return sign * int(value, 8)

                else:
                    return sign * int(value, 10)

        else:
            # have something else
            return value

    def gobble(self, expr):
        """Return the given expression a token at a time allowing for string
        quoting and anonymous functions"""

        instring = False
        stringConst = False
        buff = ''

        while expr:
            char = expr[0]

            if not instring and char in "\t\r\n":
                expr = expr[1:]
                continue

            if char == '[' and not (instring or stringConst):
                function, expr = self._collectFunction(expr)
                yield list(self.gobble(function[1:-1]))

            elif char == '"':
                if instring:
                    if len(buff) == 0:
                        yield ""    # empty string
                        buff = ''
                        instring = False

                    elif buff[-1] == "\\":
                        buff += char

                    else:
                        yield '"' + buff + '"'  # flag it as a string with quotation marks
                        buff = ''
                        instring = False

                else:
                    instring = True

            elif char == "'":  # special string quote: '<string to space>
                stringConst = True

            elif char == ' ':
                if instring:
                    # Quoted strings can contain spaces.
                    buff += char

                elif stringConst:
                    yield '"' + buff + '"'  # flag it as a string with quotation marks
                    buff = ''
                    stringConst = False

                elif buff.strip():
                    # Given character may be a number.
                    yield self.internNumber(buff)
                    buff = ''

            elif instring or stringConst or char not in ' []':
                buff += char

            if len(expr) > 1:
                expr = expr[1:]

            else:
                expr = None

        if buff:
            if stringConst:
                yield '"' + buff + '"'  # flag it as a string with quotation marks

            else:
                yield self.internNumber(buff)
