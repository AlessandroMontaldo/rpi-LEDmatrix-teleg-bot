# Manage colors.
import datetime #for smooth functionality
from rgbmatrix import graphics


class MyColor(object):
    smoothRed = 0
    smoothGreen = 0
    smoothBlu = 0
    oldMicroS = 0
    continuum = 0

    def __init__(self, *args, **kwargs):
        self.oldMicroS = int(str(datetime.datetime.now()).split(".")[1]) #get us

    def __call__(self):
        print("call func does nothing")

    def smoothColor(self):
        us = int(str(datetime.datetime.now()).split(".")[1]) #get current microseconds
        #print(us)
        
        #if (us - self.oldMicroS < 4): #5us has not been passed
        #    return self.smoothRed, self.smoothGreen, self.smoothBlu

        #update RGB values
        self.continuum += 1
        self.continuum %= 3 * 255 #reset continuum after 3 round of 255

        if self.continuum <= 255:
            c = self.continuum
            self.smoothBlu = 255 - c
            self.smoothRed = c
        elif self.continuum > 255 and self.continuum <= 511:
            c = self.continuum - 256
            self.smoothRed = 255 - c
            self.smoothGreen = c
        else:
            c = self.continuum - 512
            self.smoothGreen = 255 - c
            self.smoothBlu = c

        #update oldMicroS
        self.oldMicroS = us
        return self.smoothRed, self.smoothGreen, self.smoothBlu

# Main function
if __name__ == "__main__":
    print("myColor.py does nothing")
        