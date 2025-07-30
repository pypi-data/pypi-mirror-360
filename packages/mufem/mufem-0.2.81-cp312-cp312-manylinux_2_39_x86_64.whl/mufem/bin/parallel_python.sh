#!/bin/bash

# Check if RUN_WITH_MPI is set
if [ -z "$RUN_WITH_MPI" ]; then
  echo "Error: RUN_WITH_MPI is not set."
  exit 1
fi

# @todo: make sure our own function is called
$MUFEM_MIRROR_DIR/bin/mpiexec -n $RUN_WITH_MPI python3 "$@"

