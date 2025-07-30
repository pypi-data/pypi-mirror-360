# Makefile for manual pages
# SPDX-FileCopyrightText: 2025 Nguyễn Gia Phong
# SPDX-License-Identifier: AGPL-3.0-or-later

.POSIX:
.PHONY: all clean install uninstall

PREFIX ?= /usr/local
BINDIR ::= $(DESTDIR)$(PREFIX)/bin
MANDIR ::= $(DESTDIR)$(PREFIX)/share/man
MAN1 ::= scadere-check.1 scadere-listen.1
MAN1FLAGS ::= -s 1 --source=Scadere --locale=en_US.UTF-8 --no-info

all: $(MAN1)

scadere-check.1: $(BINDIR)/scadere-check check.h2m
	help2man --name='TLS certificate expiration checker'\
		$(MAN1FLAGS) --include=check.h2m --output=$@ $<

scadere-listen.1: $(BINDIR)/scadere-listen listen.h2m
	help2man --name='Atom feed server to remind of TLS certificate renewal'\
		$(MAN1FLAGS) --include=listen.h2m --output=$@ $<

clean:
	rm -f $(MAN1)

install: $(MAN1:%.1=$(MANDIR)/man1/%.1)

$(MANDIR)/man1/%.1: %.1
	install -Dm 644 $< $@

uninstall:
	rm -f $(MAN:%.1=$(MANDIR)/man1/%.1)
