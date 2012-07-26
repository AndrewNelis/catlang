
import lib.basic_tests
import lib.level0


def load_stdlib(ns_dict):

    all_libs = (
            lib.basic_tests.ns,
            lib.level0.ns,
    )

    for library in all_libs:
        library.populate(ns_dict)
