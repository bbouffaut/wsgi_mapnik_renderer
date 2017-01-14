# wsgi_mapnik_renderer
Implement a apache mod_wsgi Open-Street-Map rendered based on mapnik
NB: wsgi module shall be enabled in apache

#Apache site configuration example

<VirtualHost *:80>
	# The ServerName directive sets the request scheme, hostname and port that
	# the server uses to identify itself. This is used when creating
	# redirection URLs. In the context of virtual hosts, the ServerName
	# specifies what hostname must appear in the request's Host: header to
	# match this virtual host. For the default virtual host (this file) this
	# value is not decisive as it is used as a last resort host regardless.
	# However, you must set it for any further virtual host explicitly.
	ServerName tiles-server.com
	ServerAdmin admin@tiles-server.com

	WSGIDaemonProcess tiles-server.com processes=4 threads=10 display-name=%{GROUP} user=user
	WSGIProcessGroup tiles-server.com

	WSGIScriptAlias / /path/to/wsgi_script/wsgi_renderer.py

	<Directory /path/to/wsgi_script >
		Require all granted
	</Directory>

	# Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
	# error, crit, alert, emerg.
	# It is also possible to configure the loglevel for particular
	# modules, e.g.
	#LogLevel info ssl:warn

	ErrorLog ${APACHE_LOG_DIR}/tiles-server_error.log
	CustomLog ${APACHE_LOG_DIR}/tiles-server_combined.log combined

	# For most configuration files from conf-available/, which are
	# enabled or disabled at a global level, it is possible to
	# include a line for only one particular virtual host. For example the
	# following line enables the CGI configuration for this host only
	# after it has been globally disabled with "a2disconf".
	#Include conf-available/serve-cgi-bin.conf
</VirtualHost>


