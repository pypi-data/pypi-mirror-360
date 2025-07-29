import time
# @ref https://stackoverflow.com/questions/5849800/what-is-the-python-equivalent-of-matlabs-tic-and-toc-functions


class Timer(object):
    def __init__(self, name=None):
        self.name = name

    def __enter__(self):
        self.tstart = time.time()

    def __exit__(self, type, value, traceback):
        dt = time.time() - self.tstart
        if self.name:
            print('dt [Finished][%s] >>> Elapsed: %s s' % (self.name, dt))
        else:
            print('dt >>> Elapsed: %s s' % dt)
