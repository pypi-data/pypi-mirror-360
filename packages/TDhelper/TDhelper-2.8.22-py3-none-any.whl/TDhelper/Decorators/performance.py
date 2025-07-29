import logging
import time


class performance:
    __state__ = True

    @classmethod
    def on_off(self, on=True):
        self.__state__ = on

    @classmethod
    def performance_testing(self, func):
        def wapper(*args, **kwargs):
            if self.__state__:
                start = time.clock_gettime(0)
                result = func(*args, **kwargs)
                end = time.clock_gettime(0)
                logging.info("execute function %s consuming time %f(s)." % (
                    func.__name__, end-start))
                return result
            else:
                return func(*args, **kwargs)
        return wapper
