import sys
import os

class terminalIOSTD:
    def __init__(self, file, shm):
        self.filename = f'{os.path.expanduser("~")}/.ADPIOEDGE/adpio_{file}.log'
        if shm:
            self.filename = f'/dev/shm/adpio_{file}.log'
            

    def write(self, lines):
        with open(self.filename, 'a') as f:
            f.write(lines)

    def writelines(self, lines):
        self.write(lines)
            
    def isatty(self):
        return False
    
    def close(self):
        pass

    def fileno(self):
        return 0
    
    def flush(self):
        pass

    def closed(self):
        return False
        

class terminal_web:
    def __init__(self, file, shared):
        self.terminalIO   = None

        self.out_std      = None
        self.err_std      = None

        self.file         = file
        self.shm          = shared #Shared Memory?

        self.initialize()


    def initialize(self):
        self.terminalIO = terminalIOSTD(self.file, self.shm)

        self.out_std = sys.stdout #Save System stdouts
        self.err_std = sys.stderr #Save System stdouts
   
        sys.stdout = self.terminalIO
        sys.stderr = self.terminalIO       


    def terminate(self):
        sys.stdout = self.out_std #put sys stdouts back
        sys.stderr = self.err_std #put sys stdouts back

