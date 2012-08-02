#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# catlang.py - Andrew Nelis <andrew.nelis@gmail.com>
#            - extended by Wayne Wiitanen <wiitanen@paonia.com> June, 2012
#
# An interpreter for the cat language.
#
# Usage:
#
# ./catlang.py --eval "code" - Evaluate the given source
# ./catlang.py - (no arguments) Start an interactive session.
#
# If you add a new function, be sure to add a test (or two) to the runtest
# function.
#
# LICENSE: LGPL
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License (LGPL) as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA,
# or see http://www.gnu.org/copyleft/lesser.html

__version__ = '0.7'

import sys

from cat.repl import REPL
from cat.eval import CatEval

try:
    from colorama import init, Fore
    init(autoreset=True)

    def colored(text, color=None):
        if color:
            fg_color = getattr(Fore, color.upper())
        else:
            fg_color = ''
        return fg_color + text

except ImportError:

    def colored(text, _):  # NOQA
        return text


if __name__ == '__main__':
    cat = CatEval(output_fn=colored)

    if len(sys.argv) > 1:
        if sys.argv[1] in ('-e', '--eval'):
            cat.eval(' '.join(sys.argv[2:]))
            print cat

    else:
        r = REPL(cat)
        r.run()
