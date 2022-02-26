#!/usr/bin/env bash

PROJ_PATH=$(cd "$(dirname "$0")";pwd)
APP_PATH=${PROJ_PATH}/app
JENA_PATH=${PROJ_PATH}/jena
FUSEKI_PATH=${JENA_PATH}/apache-jena-fuseki-3.16.0
FUSEKI_BASE_PATH=${FUSEKI_PATH}/run_tdb

# start jena
export FUSEKI_BASE=${FUSEKI_BASE_PATH}
cd ${FUSEKI_PATH} && ./fuseki-server &

# start KBQA app
streamlit run streamlit_app.py &
