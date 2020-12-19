from settings import debug_to_console

__all__ = [
	'Logger',
	'logger',
]

class Logger:
    def __init__(self):
        if __debug__:
            self.fp = None
            self.closed = 1

    def open(self, file: str):
        if __debug__:
            if not self.closed: raise IOError('Opening already opened file!')
            self.fp = open(file, 'wt')
            self.closed = 0
        return self

    def log(self, *msg):
        if __debug__:
            if self.closed: raise IOError('Logging after closing file!')
            items = [str(item) for item in msg]
            if debug_to_console:
                print(*items)
            for item in items:
                self.fp.write(item)
        return self

    def close(self):
        if __debug__:
            if not self.closed: raise IOError('Closing already closed file!')
            self.fp.close()
            self.closed = 1
        return self

    def __del__(self):
        self.close()

logger = Logger().open('logs/########.log')