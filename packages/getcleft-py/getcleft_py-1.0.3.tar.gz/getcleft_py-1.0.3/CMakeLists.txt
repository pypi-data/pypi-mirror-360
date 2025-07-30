# CMakeLists.txt

cmake_minimum_required(VERSION 3.15)
project(getcleft_builder C)

include(FetchContent)

FetchContent_Declare(
  GetCleftRepo
  GIT_REPOSITORY https://github.com/NRGlab/Get_Cleft.git
  GIT_TAG f223848f9471e5a7f2587044e5dd4b3e48406f27
)

FetchContent_MakeAvailable(GetCleftRepo)

add_executable(Get_Cleft_Target "${getcleftrepo_SOURCE_DIR}/Get_Cleft.c")
set_target_properties(Get_Cleft_Target PROPERTIES OUTPUT_NAME "GetCleft")

# Platform-specific configurations
if(MSVC)
    target_compile_options(Get_Cleft_Target PRIVATE /O2)
else()
    target_compile_options(Get_Cleft_Target PRIVATE -O3)
    target_link_libraries(Get_Cleft_Target PRIVATE m)
endif()

include(GNUInstallDirs)
install(TARGETS Get_Cleft_Target
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
install(FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/getcleftpy/__init__.py
    ${CMAKE_CURRENT_SOURCE_DIR}/getcleftpy/GetCleft_wrapper.py
    DESTINATION ${CMAKE_INSTALL_PREFIX}
)