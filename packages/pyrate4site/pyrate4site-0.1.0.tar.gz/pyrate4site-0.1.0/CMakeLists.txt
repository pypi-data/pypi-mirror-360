cmake_minimum_required(VERSION 3.4...3.18)
project(pyrate4site)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

add_subdirectory(pybind11)
add_subdirectory(cpp)

pybind11_add_module(pyrate4site cpp/main.cpp)


target_link_libraries(pyrate4site PRIVATE librate4site)

target_compile_definitions(pyrate4site
                           PRIVATE VERSION_INFO=${EXAMPLE_VERSION_INFO})