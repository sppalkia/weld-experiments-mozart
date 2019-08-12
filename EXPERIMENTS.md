## SOSP 2019 Experiments

This document describes how to run the main experiments in the SOSP 2019 paper.

## System Requirements

We have only tested the experiments on an m4.10xlarge Amazon EC2 instance. We
have made a public AMI that can be used to run everything, with all necessary
packages etc. pre-installed. The minimum system requirements are:

* At least 150GB of RAM
* At least 16 cores that can compile an optimized version of Intel MKL
* Running Ubuntu 16.04 with a recent Linux kernel (we've only tested it on 4.4.0)

## C Experiments

1. Follow the build instructions in the README in this directory.
2. Install Intel MKL and ImageMagick, as described below.

  #### Installing MKL

  We tested our code with MKL 2018 (Update 2). To install, visit [this link](https://software.seek.intel.com/performance-libraries) and follow the instructions below.

  1. Fill out the information requested in the form and click "Submit"
  2. In the dropdown menu stating "Please select a Product" choose "Intel Math Kernel Library for Linux"
  3. Under "Choose a Version" choose "Intel MKL 2018 (Update 2)"
  4. Click "Full Package" and follow the remaining instructions to install MKL.

  Once MKL is set up, make sure that the `$MKLROOT` environment variable is set to the correct value. On our system, it is set to the following:

  ```bash
  /opt/intel/compilers_and_libraries_2018.2.199/linux/mkl
  ```

  If this environment variable is not set, compilation of the benchmarks will fail. 

  #### Installing ImageMagick

  We use ImageMagick-7 in our benchmarks. To install:

  1. Make sure build tools are available and up to date:

    ```bash
    sudo apt-get update
    sudo apt-get install build-essential
    ```

  2. Install ImageMagick from source:

    ```bash
    wget https://www.imagemagick.org/download/ImageMagick.tar.gz
    tar xvzf ImageMagick.tar.gz
    # Your version may be different, but the major version should be 7
    cd ImageMagick-7.0.8-59
    ```

  3. Configure, build and install:

    ```bash
    ./configure
    make
    sudo make install
    ```

  4. Make sure everything worked:

    ```bash
    magick -version
    Version: ImageMagick 7.xxxxx
    ...
    ```
3. Build the annotated libraries. Assuming `$SA_HOME` is the root directory:

  ```bash
  cd $SA_HOME/c/lib/composer_mkl
  make
  cd $SA_HOME/c/lib/ImageMagick
  make
  ```

4. Run the benchmarks using the provided script. This will also download all
   the data needed to run the benchmarks. Make sure you change to the correct
   directory first, because some things use relative directories:

  ```bash
  cd $SA_HOME/c/benchmarks/
  ./run-all.sh
  ```

  The results will be in the `$SA_HOME/composer/c/benchmarks/results` directory.

## Python Experiments (Mozart and Numba, Native Library, and Bohrium baselines)

1. To run the Python experiments, go to the benchmark directory and run the provided `run-all.sh` script. This will set up an environment and
download the necessary data, and run everything:

  ```bash
  cd $SA_HOME/composer/python/benchmarks
  ./run-all.sh
  ```
  
  The results will be in the `$SA_HOME/composer/python/benchmarks/results` directory.

## Weld Baselines

Since Weld requires slightly different Python distribution requirements and other dependencies, we run them in a separate virtual environment. Make sure everything
is run from the appropriate directory (e.g., `$HOME` if `cd $HOME` is specified):

1. Clone the Weld repo. Make sure you are the `v0.2.0` branch, which supports multi-threading.

  ```bash
  cd $HOME
  git clone -b v0.2.0 git@github.com:weld-project/weld.git
  ```

2. Make sure LLVM is installed and that everything is configured properly. In particular, you should be able to run `llvm-config --version` and see `6.x.x`. If you don't have
LLVM, run the following, which downloads all the Weld requirements:

  ```bash
  wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key | sudo apt-key add -
  sudo apt-add-repository "deb http://apt.llvm.org/xenial/ llvm-toolchain-xenial-6.0 main"
  sudo apt-get update
  sudo apt-get install llvm-6.0-dev clang-6.0 zlib1g-dev
  sudo ln -s /usr/bin/llvm-config-6.0 /usr/local/bin/llvm-config
  ```

3. Build Weld. You should already have Rust installed for Mozart:

  ```bash
  cd $HOME/weld
  cargo build --release
  ```

4. Clone and run the experiments. This will build the Weld versions of Pandas and NumPy, setup
a environment, install the requirements, and run each experiment:

  ```bash
  todo
  ```

This should conclude the main results fo the paper. Please email shoumik@cs.stanford.edu with any questions.

## Other Experiments and Microbenchmarks

