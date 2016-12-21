TARGETS = VMtranslate

all: $(TARGETS)

VMtranslate: Main.py
	cp -f $< $@
	chmod +x $@