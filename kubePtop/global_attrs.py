
class GlobalAttrs:

    env_connection_method = ""

    env_prometheus_pod_name = ""
    env_prometheus_pod_port = "9090"
    env_prometheus_pod_namespace = "default"
    env_kube_config_file = ""

    env_prometheus_server = "??"
    env_basic_auth_enabled = False
    env_prometheus_username = ""
    env_prometheus_password = ""
    env_insecure = False

    log_dir = "/tmp/"
    log_file = "kptop.log"

    exceptions_num = 0
    session = None

    initial_message = "Loading ..."

    node_exporter_node_label = "node" #"kubernetes_node"
    kubernetes_exporter_node_label = "instance"
    live_update_interval = 8
    start_graphs_with_zero = True
    graphs_width = 45

    default_dashboards_dir = "/var/kptop/dashboards"
    default_commands_dir = "/var/kptop/commands"

    debug = False
    version = "v0.0.9"

    def __init__(self):
        pass
