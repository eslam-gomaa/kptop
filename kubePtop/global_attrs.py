
class GlobalAttrs:
    env_prometheus_server = "..."
    env_basic_auth_enabled = False
    env_prometheus_username = None
    env_prometheus_password = None
    env_insecure = False
    
    log_file_path = "/tmp/kptop.log"
    exceptions_num = 0
    session = None

    node_exporter_node_label = "node" #"kubernetes_node"
    kubernetes_exporter_node_label = "instance"
    live_update_interval = 8
    start_graphs_with_zero = True
    
    debug = False

    def __init__(self):
        pass
