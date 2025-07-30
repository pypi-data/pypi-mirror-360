cmake_minimum_required(VERSION 3.11.0)
project(simplex)

if(WIN32)
elseif(APPLE)
    find_package(Boost REQUIRED)
    find_package(MPI)
else()
    find_package(MPI)
endif()

set(SRC
    common/bessel.cpp
    common/common.cpp
    common/data_container.cpp
    common/fast_fourier_transform.cpp
    common/fftsg.cpp
    common/fftsg2d.cpp
    common/function_statistics.cpp
    common/id_field_profile.cpp
    common/interpolation.cpp
    common/json_writer.cpp
    common/mpi_by_thread.cpp
    common/mpi_dummy.cpp
    common/optimization.cpp
    common/print_calculation_status.cpp
    common/quadrature.cpp
    common/randomutil.cpp
    common/undulator_data_manipulation.cpp
    common/wigner_function_disc.cpp
    simplex_src/lattice_operations.cpp
    simplex_src/main.cpp
    simplex_src/particle_handler.cpp
    simplex_src/radiation_handler.cpp
    simplex_src/rocking_curve.cpp
    simplex_src/simplex_config.cpp
    simplex_src/simplex_solver.cpp
    simplex_src/wakefield.cpp
)
set(HEADER
    common/bessel.h
    common/common.h
    common/data_container.h
    common/fast_fourier_transform.h
    common/function_statistics.h
    common/id_field_profile.h
    common/interpolation.h
    common/json_writer.h
    common/mpi_by_thread.h
    common/mpi_dummy.h
    common/numerical_common_definitions.h
    common/optimization.h
    common/picojson.h
    common/print_calculation_status.h
    common/quadrature.h
    common/randomutil.h
    common/undulator_data_manipulation.h
    common/wigner_function_disc.h
    simplex_src/lattice_operations.h
    simplex_src/particle_handler.h
    simplex_src/radiation_handler.h
    simplex_src/rocking_curve.h
    simplex_src/simplex_config.h
    simplex_src/simplex_input.h
    simplex_src/simplex_solver.h
    simplex_src/wakefield.h
)
if(APPLE)
set(INCCOM common simplex_src ${Boost_INCLUDE_DIRS})
else()
set(INCCOM common simplex_src)
endif()

set(TARGETS simplex_solver_nompi simplex_solver)
add_executable(simplex_solver_nompi ${SRC} ${HEADER})
add_executable(simplex_solver ${SRC} ${HEADER})
target_compile_definitions(simplex_solver_nompi PRIVATE -D__NOMPI__)
target_compile_features(simplex_solver_nompi PRIVATE cxx_std_17)
target_compile_features(simplex_solver PRIVATE cxx_std_17)

if(WIN32)
    string(REPLACE "/MD" "/MT" CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE}")
    string(REPLACE "/MDd" "/MTd" CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG}")
    target_include_directories(simplex_solver_nompi
        PRIVATE ${INCCOM})
    target_include_directories(simplex_solver
        PRIVATE ${INCCOM} $ENV{MSMPI_INC})
    target_link_directories(simplex_solver PRIVATE $ENV{MSMPI_LIB64})
    target_link_libraries(simplex_solver PRIVATE msmpi)
elseif(APPLE)
    target_compile_definitions(simplex_solver_nompi PRIVATE -D_macox)
    target_compile_definitions(simplex_solver PRIVATE -D_macox)
    target_link_libraries(simplex_solver MPI::MPI_CXX)
    execute_process(COMMAND uname "-m" OUTPUT_VARIABLE ARCH)
    string(STRIP ${ARCH} ARCH)
    if(${ARCH} STREQUAL "arm64")
        target_include_directories(simplex_solver_nompi PRIVATE ${INCCOM})
        target_include_directories(simplex_solver PRIVATE ${INCCOM})
    else()
        target_include_directories(simplex_solver_nompi PRIVATE ${INCCOM})
        target_include_directories(simplex_solver PRIVATE ${INCCOM})
    endif()
else()
    if(MPI_FOUND)
        target_link_libraries(simplex_solver MPI::MPI_CXX)
    else()
        target_compile_definitions(simplex_solver PRIVATE -D__NOMPI__)
    endif()
    target_include_directories(simplex_solver_nompi PRIVATE ${INCCOM})
    target_include_directories(simplex_solver PRIVATE ${INCCOM})
endif()

install(TARGETS ${TARGETS} RUNTIME DESTINATION .)