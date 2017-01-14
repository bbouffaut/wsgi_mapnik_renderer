#!/usr/bin/env python
# Source is GPL, credit goes to Nicolas Pouillon
# comments goes to sylvain letuffe org (" " are replaced by @ and . )
# fichier execute par mod_python. handle() est le point d'entree.

import os, os.path
from gen_tile import MapMaker

zmax=20
renderer = MapMaker("/srv/OpenTopoMap/mapnik-16.04/opentopomap.xml", zmax)

def handle(req):
    from mod_python import apache, util
    path = os.path.basename(req.filename)+req.path_info

    # strip .png
    script, right = path.split(".", 1)
    new_path, ext = right.split(".", 1)
    rien, style, z, x, y = new_path.split('/', 4)


    if style in renderers:
        req.status = 200
        req.content_type = 'image/png'
        z = int(z)
        x = int(x)
        y = int(y)
	#req.content_type = 'text/plain'
	#req.write(renderers[style])
	#return apache.OK
	if z<13:
	  cache=True
	else:
	  cache=False
        req.write(renderer.genTile(x, y, z, ext, cache))

    else:
        req.status = 404
        req.content_type = 'text/plain'
        req.write("No such style")
    return apache.OK
