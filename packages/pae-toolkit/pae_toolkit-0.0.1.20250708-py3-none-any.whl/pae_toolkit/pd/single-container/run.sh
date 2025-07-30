#!/bin/bash
export LD_LIBRARY_PATH=/usr/local/Ascend/driver/lib64/driver:/usr/local/Ascend/driver/lib64/common:$LD_LIBRARY_PATH
source /usr/local/Ascend/ascend-toolkit/set_env.sh
source /usr/local/Ascend/nnal/atb/set_env.sh
source /usr/local/Ascend/atb-models/set_env.sh
source /usr/local/Ascend/mindie/set_env.sh
export HSECEASY_PATH=/usr/local/Ascend/mindie/latest/mindie-service/lib/

export MINDIE_LOG_TO_STDOUT=1
export PD_MODE=0 # 0:分离; 3:混合
export MINDIE_INFER_MODE=dmi
export MINDIE_MS_GEN_SERVER_PORT=false
export POD_IP=127.0.0.1
export CONTAINER_IP=127.0.0.1


export PD_CONF_DIR=/home/infer/pd
chmod 640 $PD_CONF_DIR/*.json

export ATB_LLM_HCCL_ENABLE=1
export PD_MODE=0
export HCCL_OP_EXPANSION_MODE="AIV"
ATB_SHARE_MEMORY_NAME_SUFFIX=0 ./bin/mindieservice_daemon --config-file $PD_CONF_DIR/config_p0.json &
ATB_SHARE_MEMORY_NAME_SUFFIX=1 ./bin/mindieservice_daemon --config-file $PD_CONF_DIR/config_d0.json &

export MINDIE_MS_COORDINATOR_CONFIG_FILE_PATH=$PD_CONF_DIR/ms_coordinator.json
cd bin && ./ms_coordinator $POD_IP 1025 &

export GLOBAL_RANK_TABLE_FILE_PATH=$PD_CONF_DIR/global_rank_table_file.json
export MINDIE_MS_CONTROLLER_CONFIG_FILE_PATH=$PD_CONF_DIR/ms_controller.json
MINDIE_LOG_LEVEL=DEBUG MINDIE_LOG_TO_STDOUT=1 ./bin/ms_controller

# npu-smi info -t topo


install net-tools
# netstat -altuinp
netstat -tunl