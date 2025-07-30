import logging
import contextlib

# the following code emulates ioproc behavior with minimal performance penalty. This makes ioproc actions useable outside of an ioproc installation.
def action(_):
    def __outer_wrapper__(f):
        def __inner_wrapper__(*args, **kwargs):
            return f(*args, **kwargs)
        return __inner_wrapper__
    return __outer_wrapper__

mainlogger = logging.getLogger('mainlogger')

@contextlib.contextmanager
def overwrite(dmgr):
    yield
