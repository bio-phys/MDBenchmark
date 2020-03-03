#!/bin/bash
set -euo pipefail

mkdir -p $HOME/.matplotlib
echo "backend: TkAgg" > $HOME/.matplotlib/matplotlibrc
