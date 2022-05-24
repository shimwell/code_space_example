FROM mcr.microsoft.com/vscode/devcontainers/miniconda:0-3


RUN conda install -c conda-forge mamba
RUN mamba install -c conda-forge openmc
RUN pip install neutronics_material_maker openmc_data openmc_data_downloader

RUN download_nndc
