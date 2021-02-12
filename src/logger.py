from settings import debug_to_console

__all__ = [
    'Logger',
    'logger',
]


class Logger:
    def __init__(self):
        self.iostream = None
        self.closed = True
        self.enabled = __debug__ or 1
        self.masters = []

    def nest(self, master):
        if master not in self.masters:
            self.masters.append(master)
        return self

    def enable(self):
        self.enabled = True
        return self

    def disable(self):
        self.enabled = False
        return self

    def open(self, file: str):
        if not self.closed:
            raise IOError('Opening already opened file!')
        self.iostream = open(file, 'wt')
        self.closed = 0
        return self

    def log(self, *msg):
        if self.closed:
            raise IOError('Logging after closing file!')
        if self.enabled:
            items = [str(item) for item in msg]
            if debug_to_console:
                print(*items)
            for item in items:
                self.iostream.write(item + '\n')
            for master in self.masters:
                master.log(*msg)
        return self

    def close(self):
        if self.closed:
            raise IOError('Closing already closed file!')
        self.iostream.close()
        self.closed = 1
        return self

    def __del__(self):
        if not self.closed():
            self.close()


logger = Logger()\
    .open('logs/########.log')\

if __name__ == "__main__":
    print("This module is not for direct call!")
