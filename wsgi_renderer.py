#!/usr/bin/env python
import sys, os, re
directory = os.path.split(__file__)[0]
import site
site.addsitedir(directory)

import wsgi_mapnik

#print >> sys.stderr, 'Loading app...'


def render_tile(environ,tile_uri,x, y, z):

#    print >> sys.stderr, 'render_tile x={},y={},z={}'.format(str(x),str(y),str(z))
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
    	
    render_size = wsgi_mapnik.render_size
    environ['m'].resize(render_size,render_size)
    environ['m'].zoom_to_box(bbox)

    if(environ['m'].buffer_size < 128):
        environ['m'].buffer_size = 128

    # Render image with default Agg renderer
#    print >> sys.stderr, 'render_tile STAGE 3...'
    environ['mapnik'].render_to_file(environ['m'], tile_uri)
#    print >> sys.stderr, 'render_tile DONE!'

def not_found(environ, start_response):
    """Called if no URL matches."""
#    print >> sys.stderr, 'Not Found error'
    start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
    return ['Not Found']


def launch_rendering(environ,tile_uri,x,y,z):
#    print >> sys.stderr, 'create tile_uri={}'.format(tile_uri)
    environ['mapnik'] = wsgi_mapnik.mapnik
    environ['m'] = m = wsgi_mapnik.m
    environ['prj'] = wsgi_mapnik.prj
    environ['tileproj'] = wsgi_mapnik.tileproj
        
    render_tile(environ,tile_uri,x,y,z)


def process_request(environ,start_response,z,x,y):
#    print >> sys.stderr, 'Entering process_request with z={},x={},y={}'.format(z,x,y)
    # check if we have directories in place
    zoom = "%s" % z
#    print >> sys.stderr, 'dir={}'.format(wsgi_mapnik.tiledir + '/' + zoom)
    if not os.path.isdir(wsgi_mapnik.tiledir + '/' + zoom):
#	print >> sys.stderr, 'Create dir {}'.format(wsgi_mapnik.tiledir + '/' + zoom)
        os.mkdir(wsgi_mapnik.tiledir + '/' + zoom)

    # Validate x co-ordinate
    if (x < 0) or (x >= 2**z):
        not_found(environ,start_response)
    # check if we have directories in place
    str_x = "%s" % x
#    print >> sys.stderr, 'dir={}'.format(wsgi_mapnik.tiledir + '/' + zoom + '/' + str_x)
    if not os.path.isdir(wsgi_mapnik.tiledir + '/' + zoom + '/' + str_x):
	#print >> sys.stderr, 'Create dir {}'.format(wsgi_mapnik.tiledir + '/' + zoom + '/' + str_x)
        os.mkdir(wsgi_mapnik.tiledir + '/' + zoom + '/' + str_x)

    # Validate y co-ordinate
    if (y < 0) or (y >= 2**z):
        not_found(environ,start_response)

    str_y = "%s" % y
    tile_uri = wsgi_mapnik.tiledir + '/' + zoom + '/' + str_x + '/' + str_y + '.png'

    if not os.path.isfile(tile_uri):
	launch_rendering(environ,tile_uri,x,y,z)
    else:
    	size = os.path.getsize(tile_uri)

	if z >= 13 and size <= 20000:
		launch_rendering(environ,tile_uri,x,y,z)

    return tile_uri


def application(environ, start_response):

    path = re.split('/',environ.get('PATH_INFO', ''))
    (x,y,z) = (0,0,0)

    try:
        y_string = path.pop()
        y = int(y_string.split('.')[0])
        x = int(path.pop())
        z = int(path.pop())
    except ValueError:
        not_found(environ,start_response)   

    #print >> sys.stderr, 'z={},x={},y={}'.format(z,x,y)
        
    tile_uri = process_request(environ,start_response,z,x,y)

    the_file = open(tile_uri,'rb')
    size = os.path.getsize(tile_uri)
    #print >> sys.stderr, 'data_file len={}'.format(str(size))

    headers = [('Content-type', 'image/png'), ('Content-Length', str(size))]
    start_response('200 OK', headers)

    if 'wsgi.file_wrapper' in environ:
        return environ['wsgi.file_wrapper'](the_file , 1024) 

    else:

        def file_wrapper(fileobj, block_size=1024):
            try:
                data = fileobj.read(block_size)
                while data:
                    yield data
                    data = fileobj.read(block_size)
            finally:
                fileobj.close()

        return file_wrapper(the_file, 1024)  
