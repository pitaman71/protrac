default : autosrc initial_dbfiles.out server_flask.py dist/bundle.js

autosrc :
	mkdir -p $@

reset_dbfiles : initial_dbfiles.out
	for file in *_initial.json; do cp $$file $${file%_initial.json}.json; done

initial_dbfiles.out : generators/generate_initial_jsondb.py protrac.xml
	$^ > $@.in-progress
	mv $@.in-progress $@	

server_flask.py : generators/generate_server_flask.py protrac.xml 
	$^ > $@.in-progress
	mv $@.in-progress $@

autosrc/client.js : generators/generate_client_react.py protrac.xml 
	$^ > $@.in-progress
	mv $@.in-progress $@

start_server : server_flask.py
	/usr/local/bin/python $<

dist/bundle.js : autosrc/client.js
	cd public ; node_modules/webpack/bin/webpack.js
