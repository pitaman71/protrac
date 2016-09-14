default : autosrc autosrc/server.py

autosrc :
	mkdir -p $@

autosrc/server.py : generators/generate_python_server.py protrac.xml 
	$^ > $@.in-progress
	mv $@.in-progress $@

start_server : autosrc/server.py
	/usr/local/bin/python $<
