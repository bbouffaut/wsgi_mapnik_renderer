import sys, os
directory = os.path.split(__file__)[0]

def application(environ, start_response):
    status = "200 OK"
    # Open image file
    the_file = open(directory + "/test.png", "rb")
    # Get file size
    size = os.path.getsize(directory + "/test.png")

    response_headers = [ ('Content-Type', 'image/png'), ('Content-length', str(size)) ]

    start_response( status, response_headers ) 

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
