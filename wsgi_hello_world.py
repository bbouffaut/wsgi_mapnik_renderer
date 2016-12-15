#!/usr/bin/env python
import re

def application(environ, start_response):

	path = re.split('/',environ.get('PATH_INFO', ''))

	status = '200 OK'
	output = path.pop()
	response_headers = [('Content-type', 'text/plain'),
	('Content-Length', str(len(output)))]
	start_response(status, response_headers)

	return [output]
