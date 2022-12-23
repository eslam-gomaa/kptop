
class GlobalAttrs:
    env_prometheus_server = "??"
    env_basic_auth_enabled = False
    env_prometheus_username = None
    env_prometheus_password = None
    env_insecure = False
    
    log_dir = "/tmp/"
    log_file = "kptop.log"

    exceptions_num = 0
    session = None

    node_exporter_node_label = "node" #"kubernetes_node"
    kubernetes_exporter_node_label = "instance"
    live_update_interval = 8
    start_graphs_with_zero = True
    graphs_width = 45
    
    debug = False

    def __init__(self):
        pass