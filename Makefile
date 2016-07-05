PREFIX = /usr

PROGRAM = fritzbox-reconnect

build:

install:
	install -m 0755 $(PROGRAM).py $(PREFIX)/bin/$(PROGRAM)
