#!/usr/bin/env python3
import sys
import os
sys.path.insert(1,os.path.join(sys.path[0], '..'))
import colorsys

def line_number(n,lightness):
    n = int(n)
    if(n<=0):
        raise Exception("No Colors To Give")
    else:
        step = 1/n
        saturation = 1
        colors = []
        for i in range(0,n):
            hue = i*step
            colorTuple = colorsys.hsv_to_rgb(hue,saturation,lightness)
            colorTuple = [str(int(255*x)) for x in colorTuple]
            colorString = "rgb("+colorTuple[0]+","+colorTuple[1]+","+colorTuple[2]+")"
            colors.append(colorString)
        return(colors)

def float_range(start,stop,step):
    rangeList = []
    while stop > start:
        rangeList.append(start)
        start += step
    return(rangeList)

def high_green(n,opacity):
    n = int(n)
    if(n<=0):
        raise Exception("No Colors To Give")
    else:
        step = (.4)/n
        fRange = float_range(0,.4,step)
        fRange.reverse()
        saturation = 1
        lightness = 0.8
        colors = []
        for i in range(0,len(fRange)):
            hue = i*step
            colorTuple = colorsys.hsv_to_rgb(fRange[i],saturation,lightness)
            colorTuple = [str(int(255*x)) for x in colorTuple]
            colorString = "rgba("+colorTuple[0]+","+colorTuple[1]+","+colorTuple[2]+","+str(opacity)+")"
            colors.append(colorString)
        return(colors)

if __name__ == "__main__":
    print(high_green(sys.argv[1]))
