.PHONY: all clean

all: application-packages-all

application-packages-all:
	$(MAKE) -C application-packages all

clean:
	rm -f application-packages/*/*.aux application-packages/*/*.log application-packages/*/*.out application-packages/*/*.synctex.gz application-packages/*/*.xdv application-packages/*/*.toc application-packages/*/*.fls application-packages/*/*.fdb_latexmk

-include application-packages/application-packages.mk
