cmake_minimum_required(VERSION 3.16)
project(RealTimeTranslatorGUI)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Force ARM64 architecture for Apple Silicon
set(CMAKE_OSX_ARCHITECTURES "arm64")

# Find Qt6 packages
find_package(Qt6 REQUIRED COMPONENTS Core Widgets)

# Disable AUTOUIC since we don't have .ui files
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC OFF)
set(CMAKE_AUTORCC OFF)

# Set source files
set(SOURCES
    src/main.cpp
    src/MainWindow.cpp
    src/SettingsDialog.cpp
)

set(HEADERS
    src/MainWindow.h
    src/SettingsDialog.h
)

# Create the executable
add_executable(RealTimeTranslatorGUI ${SOURCES} ${HEADERS})

# Link Qt6 libraries
target_link_libraries(RealTimeTranslatorGUI 
    Qt6::Core
    Qt6::Widgets
)

# Copy Python bridge to build directory
configure_file(
    python/gui_backend.py 
    ${CMAKE_BINARY_DIR}/gui_backend.py 
    COPYONLY
)

# Create requirements.txt in build directory
file(WRITE ${CMAKE_BINARY_DIR}/requirements.txt 
    "speechrecognition==3.10.0\ngoogletrans==3.1.0a0\npygame==2.5.2\nsounddevice==0.4.6\nnumpy==1.24.3\nrequests==2.31.0"
)

# Set output directory
set_target_properties(RealTimeTranslatorGUI PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
)