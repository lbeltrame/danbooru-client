include (KDE4Defaults)

set(DANBOORU_FILES 
    __init__.py
    actiondialog.py
    connectwidget.py
    danbooru_client.py
    danboorupostwidget.py
    danbooru2nepomuk.py
    fetchwidget.py
    mainwindow.py
    poolwidget.py
    preferences.py
    tagwidget.py
    thumbnailarea.py
    thumbnailview.py

)

foreach ( _PYFILE ${DANBOORU_FILES} )
    # Glob gets absolute file paths!
    GET_FILENAME_COMPONENT(_filename ${_PYFILE} NAME)
    python_install ( ${_filename}  ${PYTHON_SITE_PACKAGES_DIR}/danbooru)
endforeach ( _PYFILE )

install ( FILES danbooruui.rc DESTINATION ${DATA_INSTALL_DIR}/danbooru_client)
install ( FILES img/logo_resized.png DESTINATION ${DATA_INSTALL_DIR}/danbooru_client RENAME logo.png)

#Copied and modified from FindPyKDE4.cmake
INSTALL(CODE "EXECUTE_PROCESS(COMMAND ${CMAKE_COMMAND} -DTARGET=${PYTHON_SITE_PACKAGES_DIR}/danbooru/danbooru_client.py -DLINK_NAME=${BIN_INSTALL_DIR}/danbooru_client -P ${current_module_dir}/create_exe_symlink.cmake)" )

INSTALL(CODE "EXECUTE_PROCESS(COMMAND ${CMAKE_COMMAND} -DTARGET=${PYTHON_SITE_PACKAGES_DIR}/danbooru/danbooru2nepomuk.py -DLINK_NAME=${BIN_INSTALL_DIR}/danbooru2nepomuk -P ${current_module_dir}/create_exe_symlink.cmake)" )

add_subdirectory(ui)
add_subdirectory(api)
