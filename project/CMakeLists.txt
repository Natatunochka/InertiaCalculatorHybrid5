cmake_minimum_required(VERSION 3.10)
project(InertiaCalculator LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Для Windows устанавливаем правильные флаги компиляции
if(WIN32)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

add_library(inertia SHARED
    inertia_calculator.cpp
    inertia_calculator.h
)

target_compile_definitions(inertia PRIVATE BUILDING_INERTIA_DLL)

# Убедимся, что все символы экспортируются
if(WIN32)
    set_target_properties(inertia PROPERTIES
        WINDOWS_EXPORT_ALL_SYMBOLS TRUE
    )
endif()

add_executable(inertia_cli main.cpp)
target_link_libraries(inertia_cli inertia)