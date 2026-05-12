
# Get every child directory name.
macro(get_subdectory_name dir result)
    file(GLOB sub_dirs RELATIVE ${dir} ${dir}/*)
    set(sub_dir_names "")
    foreach(sub_dir ${sub_dirs})
        if(IS_DIRECTORY ${dir}/${sub_dir})
            list(APPEND sub_dir_names ${sub_dir})
        endif()
    endforeach()
    set(${result} ${sub_dir_names})
endmacro()

# Check whether a child directory contains CMakeLists.txt.
macro(has_cmakelists_file dir has_cmakelists)
    set(${has_cmakelists} OFF)
    file(GLOB is_exist_cmakelists_file RELATIVE ${dir} ${dir}/CMakeLists.txt)
    if(is_exist_cmakelists_file)
        set(${has_cmakelists} ON)
    endif()
endmacro()

# Add every child directory that contains CMakeLists.txt.
macro(auto_subdirectory)
    set(dir ${CMAKE_CURRENT_SOURCE_DIR})
    get_subdectory_name(${dir} sub_dir_names)
    foreach(sub_dir_name ${sub_dir_names})
        has_cmakelists_file(${dir}/${sub_dir_name} has_cmakelists)
        if(${has_cmakelists})
            add_subdirectory(${sub_dir_name})
        endif()
    endforeach()
endmacro()
