#!/bin/bash
docker run -it --rm \
    -u root \
    -w /usr/local/Ascend/mindie/latest/mindie-service \
    --privileged=true \
    --shm-size=1000g \
    --net=host \
    -v /usr/local/Ascend/driver:/usr/local/Ascend/driver \
    -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
    -v /usr/local/dcmi:/usr/local/dcmi \
    -v /usr/local/sbin:/usr/local/sbin \
    -v /usr/share/zoneinfo/Asia/Shanghai:/etc/localtime \
    -v /etc/ascend_install.info:/etc/ascend_install.info \
    -v /tmp:/tmp \
    -v /data:/data \
    -v /home:/home \
    -v /root/.cache:/root/.cache \
    a74993158554 bash
