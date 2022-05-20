# This Dockerfile creates an enviroment / dependancies needed to run the
# activation_env.

# This Dockerfile can be build locally or a prebuild image can be downloaded

# To build this Dockerfile into a docker image:
# docker build -t activation_env .


# To build this Dockerfile with different options --build-arg can be used
# --build-arg compile_cores=1
#   int
#   number of cores to compile codes with
# --build-arg build_double_down=OFF
#   ON OFF
#   controls if DAGMC is built with double down (ON) or not (OFF). Note that if double down is OFF then Embree is not included
# --build-arg include_avx=true
#   true false
#   controls if the Embree is built to use AVX instruction set (true) or not (false). AVX is not supported by all CPUs 

#  docker build -t activation_env --build-arg compile_cores=7 --build-arg build_double_down=OFF .
#  docker build -t activation_env:embree --build-arg compile_cores=7 --build-arg build_double_down=ON --build-arg include_avx=true .
#  docker build -t activation_env:embree-avx --build-arg compile_cores=7 --build-arg build_double_down=ON --build-arg include_avx=false .

# for local testing I tend to use this build command
# docker build -t activation_env --build-arg compile_cores=14 --build-arg build_double_down=ON .
# and then run with this command
# docker run -p 8888:8888 activation_env

# This can't be done currently as the base images uses conda installs for moab / dagmc which don't compile with OpenMC
FROM mcr.microsoft.com/vscode/devcontainers/miniconda:0-3


RUN apt-get --yes update && apt-get --yes upgrade

                          # eigen3 needed for DAGMC
RUN apt-get --yes install libeigen3-dev \
                        #   sudo  \
                          # sudo is needed during the NJOY install
                          git \
                          wget \
                          gfortran \
                          g++ \
                          mpich \
                          libmpich-dev \
                          libhdf5-serial-dev \
                          libhdf5-mpich-dev \
                          hdf5-tools \
                          imagemagick \
                          cmake \
                          # libnetcdf-dev is needed to allow NETCDF on MOAB which helps with tet meshes in OpenMC
                          libnetcdf-dev \
                          # libtbb-dev required for DAGMC
                          libtbb-dev \
                          # libglfw3-dev required for DAGMC
                          libglfw3-dev \
                          # needed for CadQuery functionality
                          libgl1-mesa-glx \
                          # needed for CadQuery functionality
                          libgl1-mesa-dev \
                          # needed for CadQuery functionality
                          libglu1-mesa-dev \
                          # needed for CadQuery functionality
                          freeglut3-dev \
                          # needed for CadQuery functionality
                          libosmesa6 \
                          # needed for CadQuery functionality
                          libosmesa6-dev \
                          # needed for CadQuery functionality
                          libgles2-mesa-dev \
                          # needed for Gmsh functionality
                          libxft2




# needed for openmc
RUN pip install --upgrade numpy
RUN pip install cmake

# Clone and install MOAB
RUN mkdir MOAB && \
    cd MOAB && \
    git clone  --single-branch --branch 5.3.1 --depth 1 https://bitbucket.org/fathomteam/moab.git && \
    mkdir build && \
    cd build && \
    cmake ../moab -DENABLE_HDF5=ON \
                  -DENABLE_NETCDF=ON \
                  -DENABLE_FORTRAN=OFF \
                  -DENABLE_BLASLAPACK=OFF \
                  -DBUILD_SHARED_LIBS=OFF \
                  -DCMAKE_INSTALL_PREFIX=/MOAB && \
    make -j"$compile_cores" &&  \
    make -j"$compile_cores" install && \
    cmake ../moab -DENABLE_HDF5=ON \
                  -DENABLE_PYMOAB=ON \
                  -DENABLE_FORTRAN=OFF \
                  -DBUILD_SHARED_LIBS=ON \
                  -DENABLE_BLASLAPACK=OFF \
                  -DCMAKE_INSTALL_PREFIX=/MOAB && \
    make -j"$compile_cores" install && \
    cd pymoab && \
    bash install.sh && \
    python setup.py install
    # the following rm command appears to remove libraries that are need to use
    # pymoab so this has been commented out for now
    # rm -rf /MOAB/moab /MOAB/build

ENV PATH=$PATH:/MOAB/bin
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/MOAB/lib


# DAGMC version develop install from source
RUN mkdir DAGMC && \
    cd DAGMC && \
    git clone --single-branch --branch v3.2.1 --depth 1 https://github.com/svalinn/DAGMC.git && \
    mkdir build && \
    cd build && \
    cmake ../DAGMC -DBUILD_TALLY=ON \
                   -DMOAB_DIR=/MOAB \
                   -DBUILD_STATIC_EXE=OFF \
                   -DBUILD_STATIC_LIBS=OFF \
                   -DCMAKE_INSTALL_PREFIX=/DAGMC/ \
    make -j"$compile_cores" install && \
    rm -rf /DAGMC/DAGMC /DAGMC/build

ENV PATH=$PATH:/DAGMC/bin
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/DAGMC/lib


# installs OpenMc from source
RUN cd /opt && \
    # switch back to tagged version when 0.13.1 is released as develop depletion is used
    # git clone --single-branch --branch v0.13.0 --depth 1 https://github.com/openmc-dev/openmc.git && \
    git clone --single-branch --branch develop --depth 1 https://github.com/openmc-dev/openmc.git && \
    cd openmc && \
    mkdir build && \
    cd build && \
    cmake -DOPENMC_USE_DAGMC=ON \
          -DDAGMC_ROOT=/DAGMC \
          -DHDF5_PREFER_PARALLEL=OFF .. && \
    make -j"$compile_cores" && \
    make -j"$compile_cores" install && \
    cd /opt/openmc/ && \
    pip install .


RUN pip install openmc_data

RUN convert_nndc71
RUN generate_endf71_chain
ENV OPENMC_CROSS_SECTIONS=/nndc-b7.1-hdf5/cross_sections.xml

# Copy over the local repository files
WORKDIR /tasks

COPY 1_create_cad_enviroment.sh /tasks
COPY 2_create_geometry.py /tasks
COPY 4_simulate_depletion.py /tasks
COPY 5_post_process_results.py /tasks
