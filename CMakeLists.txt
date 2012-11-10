project(danbooru_client)
set(PROGRAM_VERSION 1.0.2)
set(CMAKE_BUILD_TYPE "Release")

find_package(KDE4)
find_package(PythonInterp)
find_package(PyQt4)
find_package(PyKDE4)
include(PythonMacros)

install ( FILES danbooru_client.desktop DESTINATION ${XDG_APPS_INSTALL_DIR} )

add_subdirectory( danbooru )
add_subdirectory( po )

macro_log_feature(KDE4_FOUND "kdelibs" "KDE Development Platform"
                  "http://www.kde.org" TRUE ""
                  "Required to run Danbooru Client")
macro_log_feature(PYTHONINTERP_FOUND "Python" "The Python interpreter"
                  "http://python.org" TRUE ""
                  "Required to run Danbooru Client")
macro_log_feature(PYQT4_FOUND "PyQt" "The PyQt libraries"
                  "http://www.riverbankcomputing.com" TRUE ""
                  "Required to run Dabooru Client")
macro_log_feature(PYKDE4_FOUND "PyKDE4" "The PyKDE4 bindings"
                  "http://www.kde.org" TRUE ""
                  "Required to run Danbooru Client")

macro_display_feature_log()