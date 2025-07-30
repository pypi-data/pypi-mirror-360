import json
import os
import shlex
import subprocess
from pathlib import Path


class Config:
    start_npu_id: int
    p_node_num: int
    npu_num_per_p_node: int
    d_node_num: int
    npu_num_per_d_node: int
    docker_image: str
    model_path: str


PORT_RANGE_START = 1035
PORT_NUM_PER_SERVER = 4


def preprocess_config(
    config: dict[str, dict], model_path: str, devices: list[list[int]] = [[0, 1], [2, 3]]
):
    port_start = PORT_RANGE_START
    for i in range(3):
        ServerConfig = config["ServerConfig"]
        ServerConfig["ipAddress"] = "127.0.0.1"
        ServerConfig["managementIpAddress"] = ServerConfig["ipAddress"]
        ServerConfig["httpsEnabled"] = False
        ServerConfig["inferMode"] = "dmi"
        ServerConfig["interCommTLSEnabled"] = False
        ServerConfig["port"] = port_start
        port_start += 1
        ServerConfig["managementPort"] = port_start
        port_start += 1
        ServerConfig["metricsPort"] = port_start
        port_start += 1
        ServerConfig["interCommPort"] = port_start
        port_start += 1

        BackendConfig = config["BackendConfig"]
        BackendConfig["interNodeTLSEnabled"] = False
        BackendConfig["npuDeviceIds"] = [devices[i]]

        ModelDeployConfig = BackendConfig["ModelDeployConfig"]
        ModelDeployConfig["maxSeqLen"] = 2048
        ModelDeployConfig["maxInputTokenLen"] = 1024
        ModelDeployConfig["truncation"] = True
        for ModelConfig in ModelDeployConfig["ModelConfig"]:
            ModelConfig["modelWeightPath"] = model_path
            ModelConfig["modelName"] = model_path.removesuffix("/").split("/")[-1]
            ModelConfig["worldSize"] = len(config["BackendConfig"]["npuDeviceIds"][0])
            # ModelConfig["plugin_params"] = '{"plugin_type":"prefix_cache"}'
            ModelConfig["tp"] = ModelConfig["worldSize"]
            # ModelConfig["kv_trans_timeout"] = 5

        ScheduleConfig = config["BackendConfig"]["ScheduleConfig"]
        ScheduleConfig["maxIterTimes"] = 24
        ScheduleConfig["maxPrefillBatchSize"] = 1
        ScheduleConfig["maxPrefillTokens"] = 65535
        ScheduleConfig["maxBatchSize"] = 50


def start_pd(config: Config):
    def generate_pd_conf(config: Config):
        cur_npu_id = config.start_npu_id
        service_config_path = "/usr/local/Ascend/mindie/latest/mindie-service/conf/config.json"
        pp = Path(service_config_path)
        for i in range(config.p_node_num + config.d_node_num):
            if i < config.p_node_num:
                npu_list = [j for j in range(cur_npu_id, cur_npu_id + config.npu_num_per_p_node)]
            else:
                npu_list = [j for j in range(cur_npu_id, cur_npu_id + config.npu_num_per_d_node)]
            cur_npu_id += len(npu_list)
            with open(service_config_path, "r") as f:
                config: dict[str, dict] = json.load(f)

            preprocess_config(config)
            p_or_d = "p" if i < config.p_node_num else "d"
            p_or_d_id = i if p_or_d == "p" else i - config.p_node_num
            with open(pp.parent / f"config_{p_or_d}{p_or_d_id}.json", "w") as f:
                json.dump(config, f, indent=4)

    def generate_controller_conf():
        pass

    def generate_coordinator_conf():
        pass

    pass


def start_pd2(config: Config):
    cmd = shlex.split("docker-compose rm")
    res = subprocess.run(cmd, capture_output=True)
    if res.returncode != 0:
        cmd = shlex.split("install docker-compose-linux-$(uname -m) /usr/bin/docker-compose")
        res = subprocess.run(cmd, shell=True, capture_output=True)
        if res.returncode != 0:
            raise Exception("install docker-compose failed")

    # 生成docker-compose.yaml
    docker_compose_yaml = f"""
services:
    coordinator:
            image: "{config.docker_image}"
            user: root
            working_dir: /app
            privileged: true
            shm_size: 100g
            environment:
                CONTAINER_IP: 172.21.0.2
            networks:
                pdnet:
                    ipv4_address: 172.21.0.2
            ports:
                - "1075:1025"
                - "1076:1026"
                - "1077:1027"
            volumes:
                - /usr/local/Ascend/driver:/usr/local/Ascend/driver
                - /usr/local/Ascend/firmware:/usr/local/Ascend/firmware
                - /usr/local/bin/npu-smi:/usr/local/bin/npu-smi
                - /usr/local/dcmi:/usr/local/dcmi
                - /usr/local/sbin:/usr/local/sbin
                - /usr/share/zoneinfo/Asia/Shanghai:/etc/localtime
                - /etc/ascend_install.info:/etc/ascend_install.info
                - /var/queue_schedule:/var/queue_schedule
                - /data:/data
                - /home:/home
                - ./docker/coordinator/:/app
            command: bash /app/run.sh
    controller:
        image: "{config.docker_image}"
        user: root
        working_dir: /app
        privileged: true
        shm_size: 100g
        depends_on:
            - coordinator
        environment:
            CONTAINER_IP: 172.21.0.3
        networks:
            pdnet:
                ipv4_address: 172.21.0.3
        volumes:
            - /usr/local/Ascend/driver:/usr/local/Ascend/driver
            - /usr/local/Ascend/firmware:/usr/local/Ascend/firmware
            - /usr/local/bin/npu-smi:/usr/local/bin/npu-smi
            - /usr/local/dcmi:/usr/local/dcmi
            - /usr/local/sbin:/usr/local/sbin
            - /usr/share/zoneinfo/Asia/Shanghai:/etc/localtime
            - /etc/ascend_install.info:/etc/ascend_install.info
            - /var/queue_schedule:/var/queue_schedule
            - /data:/data
            - /home:/home
            - ./docker/controller/:/app/
        command: bash /app/run.sh
"""
    cur_npu_id = config.start_npu_id
    npu_list = []
    for i in range(config.p_node_num + config.d_node_num):
        if i < config.p_node_num:
            npu_list = [j for j in range(cur_npu_id, cur_npu_id + config.npu_num_per_p_node)]
        else:
            npu_list = [j for j in range(cur_npu_id, cur_npu_id + config.npu_num_per_d_node)]
        cur_npu_id += len(npu_list)
        conrainer_ip = f"172.21.0.{i + 4}"
        pd_node_template = f"""
    pd{i}:
        image: "{config.docker_image}"
        user: root
        privileged: true
        shm_size: 100g
        working_dir: /app
        environment:
            NPU_DEVICES: "{",".join([str(i) for i in npu_list])}"
            CONTAINER_IP: {conrainer_ip}
            MODEL_PATH: {config.model_path}
        networks:
            pdnet:
                ipv4_address: {conrainer_ip}
        # ports:
        #     - "800$i:1025"
        #     - "801$i:1026"
        volumes:
            - /usr/local/Ascend/driver:/usr/local/Ascend/driver
            - /usr/local/Ascend/firmware:/usr/local/Ascend/firmware
            - /usr/local/bin/npu-smi:/usr/local/bin/npu-smi
            - /usr/local/dcmi:/usr/local/dcmi
            - /usr/local/sbin:/usr/local/sbin
            - /usr/share/zoneinfo/Asia/Shanghai:/etc/localtime
            - /etc/ascend_install.info:/etc/ascend_install.info
            - /var/queue_schedule:/var/queue_schedule
            - /home:/home
            - ./docker/pdnode/:/app
        command: bash /app/run.sh
"""
        docker_compose_yaml += pd_node_template
    docker_compose_yaml += """
networks:
    pdnet:
        ipam:
            config:
            - subnet: 172.21.0.0/16
"""
    with open("docker-compose.yaml", "w") as f:
        f.write(docker_compose_yaml)

    cmd = shlex.split("docker-compose up -d")

    return subprocess.run(cmd, check=True)
