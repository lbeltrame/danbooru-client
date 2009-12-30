#!/bin/bash

EXTRACTRC="/usr/bin/extractrc"
XGETTEXT="/usr/bin/xgettext --from-code=UTF-8 -C -kde -ci18n -ki18n:1 -ki18nc:1c,2 -ki18np:1,2 -ki18ncp:1c,2,3 -ktr2i18n:1 -kI18N_NOOP:1 -kI18N_NOOP2:1c,2 -kaliasLocale -kki18n:1 -kki18nc:1c,2 -kki18np:1,2 -kki18ncp:1c,2,3"
PODIR="/home/lb/Coding/pykde4/danbooru/po"
PROJECT="danbooru_client"

# invoke the extractrc script on all .ui, .rc, and .kcfg files in the sources
# the results are stored in a pseudo .py file to be picked up by xgettext.
echo "Extracting messages"
$EXTRACTRC --language=Python `find . -name \*.rc -o -name \*.ui -o -name \*.kcfg` >> rc.py
# call xgettext on all source files. If your sources have other filename
# extensions besides .py, just add them in the find call.
$XGETTEXT -L python `find . -name \*.py` -o $PODIR/${PROJECT}.pot

echo "Merging translations"
catalogs=`find po/ -name '*.po'`
for cat in $catalogs; do
	echo $cat
	msgmerge -o $cat.new $cat $PODIR/${PROJECT}.pot
	mv $cat.new $cat
done
echo "Done merging translations"

echo "Cleaning up"
rm rc.py
echo "Done"
