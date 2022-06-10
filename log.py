
import dumper


class Log:
    """
    Class to manage a simple log file. The file is opened when the LOG
    object is created. There are methods to close the file, write a
    string to the file, and write a hex dump of a 'bytes' object to
    the file.
    """
    def __init__(self, logfile: str):
        "Create and open the log file."
        self.logf = open(logfile, 'wt')
        self.is_open = True
        self.log('log opened')

    def close(self) -> None:
        "Close the log file."
        assert self.is_open
        self.log('log closed')
        self.logf.close()

    def log(self, *args) -> None:
        "write a string to the log file."
        s = ' '.join(str(x) for x in args)
        self.logf.write(s + '\n')

    def dump(self, s: str, size: int, buff: bytes) -> None:
        "Write a hexdump of a buffer, with a message, to the log file."
        assert self.is_open
        self.log(s)
        d = dumper.Hexdump()
        offset = 0
        while size:
            this = min(size, 16)
            self.logf.write(d.dump(buff[offset: offset+this]) + '\n')
            offset += this
            size -= this
            assert size >= 0
        self.log('')


def main() -> None:
    log = Log('LOG.txt')
    log.log('log message', 1, 'is', 2 + 4)
    log.dump('buff', 26, b'abcdefghijklmnopqrstuvwxyz')
    log.log('another one')
    log.close()


if __name__ == '__main__':
    main()
