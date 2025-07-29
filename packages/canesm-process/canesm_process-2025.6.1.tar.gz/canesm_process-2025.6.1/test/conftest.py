import sys


def myfunc(*args, **kwargs):
    return True


def load_ccc(*args, **kwargs):
    return True


def load_timing(*args, **kwargs):
    return True


module = type(sys)("mymodule")
module.myfunc = myfunc
module.load_ccc = load_ccc
module.load_timing = load_timing
sys.modules["mymodule"] = module
