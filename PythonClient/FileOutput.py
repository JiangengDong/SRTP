class FileOutput:
    """
    a class used for output data into a file
    """

    def __init__(self, filename):
        self.f = open(filename, 'w')
        if self.f is None:
            raise IOError

    def writefile(self, str):
        try:
            self.f.write(str)
        except BaseException:
            self.close()

    def close(self):
        self.f.close()
