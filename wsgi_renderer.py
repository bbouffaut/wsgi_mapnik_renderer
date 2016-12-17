#!/usr/bin/env python
import sys, os, re
directory = os.path.split(__file__)[0]
import site
site.addsitedir(directory)

import wsgi_mapnik

print >> sys.stderr, 'Loading app...'


def render_tile(environ,tile_uri,x, y, z):
    # Calculate pixel positions of bottom-left & top-right
    p0 = (x * 256, (y + 1) * 256)
    p1 = ((x + 1) * 256, y * 256)

    # Convert to LatLong (EPSG:4326)
    l0 = environ['tileproj'].fromPixelToLL(p0, z);
    l1 = environ['tileproj'].fromPixelToLL(p1, z);

    # Convert to map projection (e.g. mercator co-ords EPSG:900913)
    c0 = environ['prj'].forward(environ['mapnik'].Coord(l0[0],l0[1]))
    c1 = environ['prj'].forward(environ['mapnik'].Coord(l1[0],l1[1]))

    # Bounding box for the tile
    if hasattr(environ['mapnik'],'mapnik_version') and environ['mapnik'].mapnik_version() >= 800:
    	bbox = environ['mapnik'].Box2d(c0.x,c0.y, c1.x,c1.y)
    else:
    	bbox = environ['mapnik'].Envelope(c0.x,c0.y, c1.x,c1.y)
    	
	environ['m'].zoom_to_box(bbox)
	if(environ['m'].buffer_size < 128):
		environ['m'].buffer_size = 128

    # Render image with default Agg renderer
    render_size = 256
    im = environ['mapnik'].Image(render_size, render_size)
    environ['mapnik'].render(environ['m'], im)
    im.save(tile_uri, 'png256')

def not_found(environ, start_response):
    """Called if no URL matches."""
    start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
    return ['Not Found']

def process_response(environ,start_response,tile_uri):
    data = open(tile_uri, 'rb').read()
    start_response('200 OK', [('content-type', 'image/png'), ('content-length', str(len(data)))])
    return [data]


def application(environ, start_response):

    path = re.split('/',environ.get('PATH_INFO', ''))
    y_string = path.pop()
    y = int(y_string.split('.')[0])
    x = int(path.pop())
    z = int(path.pop())    

    print >> sys.stderr, path
    
    # check if we have directories in place
    zoom = "%s" % z
    if not os.path.isdir(wsgi_mapnik.tiledir + zoom):
        os.mkdir(wsgi_mapnik.tiledir + zoom)

    # Validate x co-ordinate
    if (x < 0) or (x >= 2**z):
        not_found(environ,stadirrt_response)
    # check if we have directories in place
    str_x = "%s" % x
    if not os.path.isdir(wsgi_mapnik.tiledir + zoom + '/' + str_x):
        os.mkdir(wsgi_mapnik.tiledir + zoom + '/' + str_x)

    # Validate x co-ordinate
    if (y < 0) or (y >= 2**z):
        not_found(environ,start_response)
    str_y = "%s" % y
    tile_uri = wsgi_mapnik.tiledir + zoom + '/' + str_x + '/' + str_y + '.png'

    if not os.path.isfile(tile_uri):
        environ['mapnik'] = wsgi_mapnik.mapnik
        environ['m'] = wsgi_mapnik.m
        environ['prj'] = wsgi_mapnik.prj
        environ['tileproj'] = wsgi_mapnik.tileproj
        
        render_tile(environ,tile_uri,x,y,z)

    process_response(environ,start_response,tile_uri)