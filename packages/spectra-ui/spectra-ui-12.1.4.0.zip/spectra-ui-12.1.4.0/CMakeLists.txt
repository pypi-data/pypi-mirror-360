cmake_minimum_required(VERSION 3.11.0)
project(spectra)

if(WIN32)
else()
    find_package(Eigen3 3.3 REQUIRED)
    find_package(Boost REQUIRED)
    find_package(MPI)
endif()

set(SRC
    common/bessel.cpp
    common/common.cpp
    common/data_container.cpp
    common/fast_fourier_transform.cpp
    common/fftsg.cpp
    common/fftsg2d.cpp
    common/function_digitizer.cpp
    common/function_statistics.cpp
    common/id_field_profile.cpp
    common/interpolation.cpp
    common/json_writer.cpp
    common/mpi_dummy.cpp
    common/mpi_by_thread.cpp
    common/mucal.cpp
    common/optimization.cpp
    common/print_calculation_status.cpp
    common/quadrature.cpp
    common/randomutil.cpp
    common/undulator_data_manipulation.cpp
    common/wigner4d_manipulator.cpp
    spectra_src/beam_convolution.cpp
    spectra_src/bm_wiggler_radiation.cpp
    spectra_src/coherent_radiation.cpp
    spectra_src/complex_amplitude.cpp
    spectra_src/density_fixed_point.cpp
    spectra_src/energy_convolution.cpp
    spectra_src/fel_amplifier.cpp
    spectra_src/filter_operation.cpp
    spectra_src/flux_density.cpp
    spectra_src/formats.cpp
    spectra_src/hermite_gauss_decomp.cpp
    spectra_src/hg_modal_decomp_ctrl.cpp
    spectra_src/kvalue_operation.cpp
    spectra_src/main.cpp
    spectra_src/montecarlo.cpp
    spectra_src/orbit_components_operation.cpp
    spectra_src/output_utility.cpp
    spectra_src/particle_generator.cpp
    spectra_src/power_density.cpp
    spectra_src/source_profile.cpp
    spectra_src/spatial_convolution.cpp
    spectra_src/spatial_convolution_fft.cpp
    spectra_src/spectra_config.cpp
    spectra_src/spectra_solver.cpp
    spectra_src/trajectory.cpp
    spectra_src/undulator_flux_far.cpp
    spectra_src/undulator_fxy_far.cpp
    spectra_src/volume_power_density.cpp
    spectra_src/wigner_function.cpp
)
set(HEADER
    common/bessel.h
    common/common.h
    common/data_container.h
    common/fast_fourier_transform.h
    common/function_digitizer.h
    common/function_statistics.h
    common/id_field_profile.h
    common/interpolation.h
    common/json_writer.h
    common/mucal.h
    common/mpi_by_thread.h
    common/numerical_common_definitions.h
    common/optimization.h
    common/picojson.h
    common/print_calculation_status.h
    common/quadrature.h
    common/randomutil.h
    common/undulator_data_manipulation.h
    common/wigner4d_manipulator.h
    spectra_src/beam_convolution.h
    spectra_src/bm_wiggler_radiation.h
    spectra_src/coherent_radiation.h
    spectra_src/complex_amplitude.h
    spectra_src/density_fixed_point.h
    spectra_src/energy_absorption_ratio.h
    spectra_src/energy_convolution.h
    spectra_src/fel_amplifier.h
    spectra_src/filter_operation.h
    spectra_src/flux_density.h
    spectra_src/formats.h
    spectra_src/hermite_gauss_decomp.h
    spectra_src/hg_modal_decomp_ctrl.h
    spectra_src/kvalue_operation.h
    spectra_src/montecarlo.h
    spectra_src/orbit_components_operation.h
    spectra_src/output_utility.h
    spectra_src/particle_generator.h
    spectra_src/power_density.h
    spectra_src/source_profile.h
    spectra_src/spatial_convolution.h
    spectra_src/spatial_convolution_fft.h
    spectra_src/spectra_config.h
    spectra_src/spectra_input.h
    spectra_src/spectra_solver.h
    spectra_src/trajectory.h
    spectra_src/undulator_flux_far.h
    spectra_src/undulator_fxy_far.h
    spectra_src/volume_power_density.h
    spectra_src/wigner_function.h
)
set(INCCOM common spectra_src ${Boost_INCLUDE_DIRS})

set(TARGETS spectra_solver_nompi spectra_solver)
add_executable(spectra_solver_nompi ${SRC} ${HEADER})
add_executable(spectra_solver ${SRC} ${HEADER})
target_compile_definitions(spectra_solver_nompi PRIVATE -D__NOMPI__)

if(WIN32)
    string(REPLACE "/MD" "/MT" CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE}")
    string(REPLACE "/MDd" "/MTd" CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG}")
    target_include_directories(spectra_solver_nompi
        PRIVATE ${INCCOM} $ENV{EIGENROOT} $ENV{BOOSTROOT})
    target_include_directories(spectra_solver
        PRIVATE ${INCCOM} $ENV{EIGENROOT} $ENV{BOOSTROOT} $ENV{MSMPI_INC})
    target_link_directories(spectra_solver PRIVATE $ENV{MSMPI_LIB64})
    target_link_libraries(spectra_solver PRIVATE msmpi)
elseif(APPLE)
    target_link_libraries(spectra_solver_nompi Eigen3::Eigen)
    target_link_libraries(spectra_solver Eigen3::Eigen MPI::MPI_CXX)
    target_compile_features(spectra_solver_nompi PRIVATE cxx_std_17)
    target_compile_features(spectra_solver PRIVATE cxx_std_17)
    execute_process(COMMAND uname "-m" OUTPUT_VARIABLE ARCH)
    string(STRIP ${ARCH} ARCH)
    if(${ARCH} STREQUAL "arm64")
        target_include_directories(spectra_solver_nompi PRIVATE ${INCCOM})
        target_include_directories(spectra_solver PRIVATE ${INCCOM})
    else()
        target_include_directories(spectra_solver_nompi PRIVATE ${INCCOM})
        target_include_directories(spectra_solver PRIVATE ${INCCOM})
    endif()
else()
    target_link_libraries(spectra_solver_nompi Eigen3::Eigen pthread)
    if(MPI_FOUND)
        target_link_libraries(spectra_solver Eigen3::Eigen MPI::MPI_CXX pthread)
    else()
        target_compile_definitions(spectra_solver PRIVATE -D__NOMPI__)
        target_link_libraries(spectra_solver Eigen3::Eigen pthread)
    endif()
    target_include_directories(spectra_solver_nompi PRIVATE ${INCCOM})
    target_include_directories(spectra_solver PRIVATE ${INCCOM})
endif()

install(TARGETS ${TARGETS} RUNTIME DESTINATION .)