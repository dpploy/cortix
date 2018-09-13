#!/bin/sh
set -ex

SUNDIALS=sundials-2.7.0
SUNDIALS_FILE=$SUNDIALS.tar.gz
SUNDIALS_URL=http://computation.llnl.gov/projects/sundials-suite-nonlinear-differential-algebraic-equation-solvers/download/$SUNDIALS_FILE
PRECISION="${SUNDIALS_PRECISION:-double}"
INDEX_TYPE="${SUNDIALS_INDEX_TYPE:-int32_t}"

wget "$SUNDIALS_URL"

tar -xzvf "$SUNDIALS_FILE"

cd $SUNDIALS
mkdir sundials_build
cd sundials_build

cmake -DCMAKE_INSTALL_PREFIX=/usr -DMPI_ENABLE=ON -DLAPACK_ENABLE=ON -DSUNDIALS_INDEX_TYPE="$INDEX_TYPE" -DSUNDIALS_PRECISION="$PRECISION" -DBUILD_ARKODE:BOOL=OFF -DEXAMPLES_ENABLE:BOOL=OFF -DEXAMPLES_INSTALL:BOOL=OFF ..
make -j$(nproc)
sudo make install
