class FileOutput:
    """
    a class used for output data into a file
    """

    def writefile(self, filename, str):
        f = open(filename, "a")
        try:
            f.write(str)
        finally:
            f.close()