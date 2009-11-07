project(danbooru_client) 
set(PROGRAM_VERSION 0.4)
set (CMAKE_BUILD_TYPE "Release")

find_package(KDE4 REQUIRED)
find_package(PythonLibrary REQUIRED)
find_package(PyQt4 REQUIRED)
find_package(PyKDE4 REQUIRED)
include(PythonMacros)

install ( FILES danbooru_client.desktop DESTINATION ${XDG_APPS_INSTALL_DIR} )

add_subdirectory( danbooru )
