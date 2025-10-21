cmake_minimum_required(VERSION 3.10)

project(flackie)

add_executable(flackie main.cpp)

target_include_directories(flackie PRIVATE ${CMAKE_SOURCE_DIR}/include)

find_package(TagLib QUIET)
if(TagLib_FOUND)
	target_link_libraries(flackie PRIVATE TagLib::TagLib)
	target_compile_definitions(flackie PRIVATE HAVE_TAGLIB)
endif()