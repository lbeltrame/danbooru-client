include (KDE4Defaults)

set(DANBOORU_FILES
        __init__.py
	test_api.py
)

foreach ( _PYFILE ${DANBOORU_FILES} )
        # Glob gets absolute file paths!
        GET_FILENAME_COMPONENT(_filename ${_PYFILE} NAME)
        python_install ( ${_filename}  ${PYTHON_SITE_PACKAGES_DIR}/danbooru/test)
endforeach ( _PYFILE )

INSTALL ( FILES post/index.json DESTINATION ${PYTHON_SITE_PACKAGES_DIR}/danbooru/test/post)
