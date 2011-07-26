include (KDE4Defaults)

set (API_FILES
	__init__.py 
    remote.py
    containers.py
    utils.py
)

foreach ( _API_FILE ${API_FILES})
    GET_FILENAME_COMPONENT(_filename ${_API_FILE} NAME)
	python_install( ${_filename} ${PYTHON_SITE_PACKAGES_DIR}/danbooru/api)
endforeach ( _API_FILE )

