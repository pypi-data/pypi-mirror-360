#! /usr/bin/env bash
#
# Copyright (C) 2025 ASTRON (Netherlands Institute for Radio Astronomy)
# SPDX-License-Identifier: Apache-2.0
#

# This file's directory is used to determine the station control directory
# location.
if [ -z ${BASH_SOURCE} ]; then
  BASH_SOURCE=${(%):-%x}
fi

ABSOLUTE_PATH=$(realpath $(dirname ${BASH_SOURCE}))

# Create a virtual environment directory if it doesn't exist
VENV_DIR="${ABSOLUTE_PATH}/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate the virtual environment
source "$VENV_DIR/bin/activate"
python -m pip install pre-commit
python -m pip install "tox>=4.21.0"

# Install git pre-commit pre-push hook
if [ ! -f "${ABSOLUTE_PATH}/.git/hooks/pre-push.legacy" ]; then
  source "${ABSOLUTE_PATH}/bin/install-hooks/pre-commit.sh"
fi
