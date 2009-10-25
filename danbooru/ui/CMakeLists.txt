include (KDE4Defaults)

set (UI_FILES
	__init__.py 
	ui_connectdialog.py
      	ui_fetchdialog.py
      	ui_nepomukpage.py
	ui_actiondialog.py
      	ui_danboorupage.py
     	ui_generalpage.py
)

foreach ( _UI_FILE ${UI_FILES})
	GET_FILENAME_COMPONENT(_filename ${_UI_FILE} NAME)
	python_install( ${_filename} ${PYTHON_SITE_PACKAGES_DIR}/danbooru/ui)
endforeach ( _UI_FILE )

