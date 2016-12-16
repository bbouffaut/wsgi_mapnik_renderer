#!/usr/bin/env python
from math import pi,cos,sin,log,exp,atan
from subprocess import call
import sys, os
import mapnik

DEG_TO_RAD = pi/180
RAD_TO_DEG = 180/pi

def minmax (a,b,c):
    a = max(a,b)
    a = min(a,c)
    return a

class GoogleProjection:
    def __init__(self,levels=18):
        self.Bc = []
        self.Cc = []
        self.zc = []
        self.Ac = []
        c = 256
        for d in range(0,levels):
            e = c/2;
            self.Bc.append(c/360.0)
            self.Cc.append(c/(2 * pi))
            self.zc.append((e,e))
            self.Ac.append(c)
            c *= 2
                
    def fromLLtoPixel(self,ll,zoom):
         d = self.zc[zoom]
         e = round(d[0] + ll[0] * self.Bc[zoom])
         f = minmax(sin(DEG_TO_RAD * ll[1]),-0.9999,0.9999)
         g = round(d[1] + 0.5*log((1+f)/(1-f))*-self.Cc[zoom])
         return (e,g)
     
    def fromPixelToLL(self,px,zoom):
         e = self.zc[zoom]
         f = (px[0] - e[0])/self.Bc[zoom]
         g = (px[1] - e[1])/-self.Cc[zoom]
         h = RAD_TO_DEG * ( 2 * atan(exp(g)) - 0.5 * pi)
         return (f,h)

def test():
    print >> sys.stderr, 'wsgi_mapnik is still loaded'

mapfile = "/srv/OpenTopoMap/mapnik-16.04/opentopomap.xml"
tiledir = "/srv/OpenTopoMap/tiles_test"
maxZoom = 15

render_size = 256
m = mapnik.Map(render_size, render_size)
m.resize(render_size, render_size)
# Load style XML
mapnik.load_map(m, mapfile, True)
# Obtain <Map> projection
prj = mapnik.Projection(m.srs)
# Projects between tile pixel co-ordinates and LatLong (EPSG:4326)
tileproj = GoogleProjection(maxZoom+1)

print >> sys.stderr, 'load wsgi_mapnik...'