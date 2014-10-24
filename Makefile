python: python.c
	gcc -g -fPIC -shared -Xlinker -export-dynamic -o python.so python.c -I../zabbix-2.4.0/include -I/usr/include/libxml2 -I/usr/include/python2.7 -lpython2.7

