# generator.py

This program generates the SQL, Protobuf, and Python data structures
needed by all the other code. It reads ih nthe YAML config file, and
outputs the language bindings.

	usage: generator [-h] [-v] files...

	options:
		-h, --help    show this help message and exit
		-v, --verbose verbose output

## example

	./generator -v users/users.yaml
