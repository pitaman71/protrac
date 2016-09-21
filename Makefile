default : autosrc server.py dist/bundle.js

autosrc :
	mkdir -p $@

server.py : generators/generate_python_server.py protrac.xml 
	$^ > $@.in-progress
	mv $@.in-progress $@

autosrc/client.js : generators/generate_jdx_client.py protrac.xml 
	$^ > $@.in-progress
	mv $@.in-progress $@

start_server : server.py
	/usr/local/bin/python $<

dist/bundle.js : autosrc/client.js
	cd public ; node_modules/webpack/bin/webpack.js
