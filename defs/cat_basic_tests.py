# Basic tests

from types import BooleanType
from cat.namespace import *
ns = NameSpace()

tests = (
    # List of ('input expression', [expected stack])
    ('clear', []),
    ('1 2 pop', [1]),
    ("pop", [] ),
    ('1 2 3 2 drop', [1]),
    ('pop 123 0b1010 0xff 017 0(3)12 0(11)2a -3.1415', [123, 10, 255, 15, 5, 32, -3.1415]),
    ('clear 3 5 +', [8]),
    ('10 9 -', [8, 1]),
    ('2 3 *', [8, 1, 6]),
    ('20 10 /', [8, 1, 6, 2]),
    ('+ + +', [17]),
    ('3 %/', [5, 2]),
    ('**', [25]),
    ('1 2 3 4 clear', []),
    ('clear 2 2 ==', [True]),
    ('clear 2 2 !=', [False]),
    ('clear 2 1 >', [True]),
    ('clear 2 1 <', [False]),
    ('clear 2 1 >=', [True]),
    ('clear 2 1 <=', [False]),
    ('clear "able" "baker"', ['able', 'baker']),
    ('clear "charlie" "dog" +', ['charliedog']),
    ('clear "a" " " "b" + +', ['a b']),
    ('clear 1 2 pop', [1]),
    ('clear 1 2 3 dup', [1, 2, 3, 3]),
    ('clear 1 2 swap', [2, 1]),
    ('clear 5 6 7 swapd', [6, 5, 7]),
    ('clear 9 8 7 dupd', [9, 8, 8, 7]),
    ('clear 9 [1 2 3] 9', [9, [1, 2, 3], 9]),
    ('clear 1 [2 +] eval', [3]),
    ('clear 1 ["t"] ["f"] if', ["t"]),
    ('clear 0 ["t"] ["f"] if', ["f"]),
    ('clear 1 2 > ["t"] ["f"] if', ["f"]),
    ('clear 9 5 range 9', [9, [0, 1, 2, 3, 4], 9]),
    ('clear 3 range dup len', [[0, 1, 2], [0, 1, 2], 3]),
    ('clear 3 range head', [0]),
    ('clear "abc" head', ["a"]),
    ('clear 3 range first', [[0, 1, 2], 0]),
    ('clear "abc" first', [ "abc", "a"]),
    ('clear 3 range last', [[0, 1, 2,], 2]),
    ('clear "abc" last', ["abc", "c"]),
    ('clear 3 range tail', [[1, 2]]),
    ('clear "abc" tail', ["bc"]),
    ('clear 3 range rest', [[1, 2]]),
    ('clear "abc" rest', ["bc"]),
    ('clear 3 range rev', [[2, 1, 0]]),
    ('clear "abcde" rev', ["edcba"]),
    ('clear 3 range [] map', [[0, 1, 2]]),
    ('clear 3 range [1 +] map', [[1, 2, 3]]),
    ('clear 5 even 0 even 1 even 8 even', [False, True, False, True]),
    ('clear 6 range [even] filter', [[0, 2, 4]]),
    ('clear 10 9 %', [1]),
    ('clear 10 5 divmod', [2, 0]),
    ('clear', []),
    ('clear 1 ++ 2 --', [2, 1]),
    ('clear 1 2 3 +rot', [3, 1, 2]),
    ('-rot', [1, 2, 3]),
    ('[swap] dip', [2, 1, 3]),
    ('clear "test text" "test" !', []),
    ('"test" @', ["test text"]),
    ('clear test', ["test text"]),
    ('clear 3 2 <<', [12]),
    ('2 >>', [3]),
    ('pop 0b10 0b11 & bin_str', ['0b10']),
    ('pop 0b100 0b010 | bin_str', ['0b110']),
    ('clear 0b110 ~ bin_str', ['0b1']),
    ('pop 0b1 as_bool', [True]),
    ('pop 10 as_float', [10.0]),
    ('as_int', [10]),
    ('pop "123" as_int', [123]),
    ('pop "123.45" as_float', [123.45]),
    ('as_list', [[123.45]]),
    ('uncons', [[], 123.45]),
    ('popd as_string', ['123.45']),
    ('clear bool_type', [BooleanType]),
    ('clear [1 2 3] list', [[1, 2, 3]]),
    ('[4 5 6] list concat', [[1, 2, 3, 4, 5, 6]]),
    ('pop [1 2 3] list 4 cons', [[1, 2, 3, 4]]),
    ('pop 42 [dup inc] [add] compose  "test" !', [42]),
    ('test apply', [85]),
    ('dec', [84]),
    ('2 /', [42]),
    ('3 divmod', [14, 0]),
    ('clear nil empty', [[], True]),
    ('pop 1 cons empty', [[1], False]),
    ('clear 12 eqz', [False]),
    ('clear 0 eqz', [True]),
    ('clear 12 gtz', [True]),
    ('clear 12 ltz', [False]),
    ('clear 12 nez', [True]),
    ('clear false', [False]),
    ("pop 'abba fetch", []),
    ('1 2 abba', [1, 2, 2, 1]),
    ("clear 'Cat/catlang.py file_exists", [True]),
    ('clear [1 2 3] list first', [[1, 2, 3], 1]),
    ('clear 123 float', [123.0]),
    ('321 cons "is ok?" cons "%f %d %s" format', ['123.000000 321 is ok?']),
    ('pop [1 2 3 4] list 2 get_at', [[1, 2, 3, 4], 3]),
    ('clear 123 hex_str', ['0x7b']),
    ('pop 41 inc', [42]),
    ("pop ['tom 'dick 'harry] list 'dick index_of", [1]),
    ('pop "this is a test string" "a test" index_of', [8]),
    ('pop 3.14 int', [3]),
    ('pop 65534 int_to_byte', [254]),
    ('pop [1 2 3] list "" list_to_str', ['123']),
    ('pop 7 2 max', [7]),
    ('2 min', [2]),
    ('pop "abc" 3 new_str', ['abcabcabc']),
    ('pop 123 neg', [-123]),
    ('pop nil', [[]]),
    ('pop true not', [False]),
    ('not', [True]),
    ('false or', [True]),
    ('pop 2 3 pair', [[2, 3]]),
    ('pop 3 2 popd', [2]),
    ('pop "1,2,3,4" py_list', [['1', '2', '3', '4']]),
    ('pop 3 [2 *] 2 repeat', [12]),
    ('pop "Hello world?" "world" "Dolly" replace_str', ['Hello Dolly?']),
    ('pop "abcabc" "b" rindex_of', [4]),
    ('pop [1 2 3 4 3 2] list 3 rindex_of', [4]),
    ('pop [1 2 3 4] 5 2 set_at', [[1, 2, 5, 4]]),
    ('size', [[1, 2, 5, 4], 1]),
    ('clear "abvdegf" str_to_list', [['a', 'b', 'v', 'd', 'e', 'g', 'f']]),
    ('pop "abc def ghi" 4 7 subseq', ['abc def ghi', 'def']),
    ('clear [1 2 3 4 5] list 6 3 swap_at', [[1, 2, 3, 6, 5], 4]),
    ('clear 3 unit', [[3]]),
    ('pop 10 [dup dec] [dup 0 neq] while', [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]),
    ('clear hash_list', [{}]),
    ("'dictn !", []),
    ("dictn 23 'a hash_set", [{'a': 23}]),
    ("42 'b hash_set", [{'a': 23, 'b': 42}]),
    ("32 'c hash_add", [{'a': 23, 'c': 32, 'b': 42}]),
    ("'c hash_contains", [{'a': 23, 'c': 32, 'b': 42}, True]),
    ("pop 'b hash_get", [{'a': 23, 'c': 32, 'b': 42}, 42]),
    ('pop hash_to_list', [[['a', 23], ['c', 32], ['b', 42]]]),
    ("'hashList !", []),
    ('dictn', [{'a': 23, 'c': 32, 'b': 42}]),
    ("clear hashList list_to_hash", [{'a': 23, 'c': 32, 'b': 42}]),
    ('clear [1 2 3 4] list 0 [add] fold', [10]),
    ('clear 0 [1 2 3 4] list [add] foreach', [10]),
    ('typeof int_type eq', [10, True]),
    ('pop typeof float_type eq', [10, False]),
    ("clear 1 [<=] papply 'test !", []),
    ('0 test apply', [True]),
    ('clear 3 test apply', [False]),
    ('clear 42.0 to_int', [42]),
    ('to_bool', [True]),
    ('clear 0 to_bool', [False]),
    ('clear [1 2 3] list [4 5 6] list [*] bin_op', [[4, 10, 18]]),
    ('clear [2 1 -1] list [-3 4 1] list cross_prod', [[5, 1, 11]]),
    ('clear -23 abs -42.12 abs 6 abs', [23, 42.12, 6]),
    ('clear [1 1 true] list all', [True]),
    ('clear [true false true] list all', [False]),
    ('clear [0 true false] list any', [True]),
    ('clear [0 false 0.0] list any', [False]),
    ('clear 122 chr', ['z']),
    ("clear ['abc, 'def, 'ghi] list 0 enum", [[[0, 'abc,'], [1, 'def,'], [2, 'ghi']]]),
    ("clear ['test 13 45.67] list [hash] map", [[hash('test'), hash(13), hash(45.67)]]),
    ("clear 'z ord", [122]),
    ("clear ['abc 'ghi 'def 'aaa 'bab] list sort", [['aaa', 'abc', 'bab', 'def', 'ghi']]),
    ("clear [1 2 3 4 5] list ['a 'b 'c 'd 'e] list zip", [[[1, 'a'], [2, 'b'], [3, 'c'], [4, 'd'], [5, 'e']]]),
    ("'zipped !", []),
    ('zipped unzip', [[1, 2, 3, 4, 5], ['a', 'b', 'c', 'd', 'e']]),
    ('clear "bob,alice,frank,princess edna,joe,doreen" "," split', [['bob', 'alice', 'frank', 'princess edna', 'joe', 'doreen']]),
    ('"**" join', ['bob**alice**frank**princess edna**joe**doreen']),
    ('clear "abcdef ghi" "" split', [['a', 'b', 'c', 'd', 'e', 'f', ' ', 'g', 'h', 'i']]),
    ('clear 1 2 3 ->aux', [1, 2]),
    ('<-aux', [1, 2, 3]),
    ('3 n->aux', []),
    ('3 n<-aux', [1, 2, 3]),
    ('clear "test text" 20 "." center', ['.....test text......']),
    ('clear "test text" 20 "." l_justify', ['test text...........']),
    ('clear "test text" 20 "." r_justify', ['...........test text']),
    ('clear "***end of tests***" "green" writeln', [])
)


@define(ns, 'runtests')
def runtests(cat):
    """
    runtests : (-- -> --)
    
    desc:
        Run a series of tests on the stack.
    tags:
        diagnostics,debug
    """
    ev  = cat.eval
    bad = 0
    n   = 0

    for expression, expected_result in tests:
        n += 1
        
        try:
            result = ev(expression)
        except Exception:
            cat.output("Exception evaluating %r" % expression, 'red')
            raise

        if result.to_list() != expected_result:
            cat.output("Error: '%s' --> expected: %r got: %r" % (
                    expression, expected_result, result.to_list()), 'red')
            bad += 1

    if not bad:
        cat.output("Performed %d tests with no errors!!" % n, 'green')

    else:
        cat.output("%d errors" % bad, 'green')

    cat.clear()

def _returnNS() :
    return ns
