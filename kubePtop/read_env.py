import os
from kubePtop.global_attrs import GlobalAttrs
gattrs = GlobalAttrs()

class ReadEnv:
    def __init__(self):
        pass

    def read_env(self):
        """
        Read Environment variables
        """

        # Mandatory ENVs
        try:
            GlobalAttrs.env_prometheus_server  = os.environ['KPTOP_PROMETHEUS_SERVER']
        except (KeyError) as e:
            raise SystemExit(f"\nERROR -- ENV not found => {e}")

        # Basic Auth ENVs
        try:
            if os.environ['KPTOP_BASIC_AUTH_ENABLED']:
                GlobalAttrs.env_basic_auth_enabled   = os.environ['KPTOP_BASIC_AUTH_ENABLED']
                GlobalAttrs.env_prometheus_username  = os.environ['KPTOP_PROMETHEUS_USERNAME']
                GlobalAttrs.env_prometheus_password  = os.environ['KPTOP_PROMETHEUS_PASSWORD']

            if GlobalAttrs.env_basic_auth_enabled:
                if (GlobalAttrs.env_prometheus_username is None or GlobalAttrs.env_prometheus_password is None):
                    raise SystemExit("INFO -- ENV: KPTOP_PROMETHEUS_USERNAME or KPTOP_PROMETHEUS_PASSWORD is missing")


            if GlobalAttrs.env_basic_auth_enabled not in [True, False, 'true', 'false']:
                print("INFO -- KPTOP_BASIC_AUTH_ENABLED > allowed options are: 'true' || 'false'")
                exit(1)

            if GlobalAttrs.env_insecure not in [True, False, 'true', 'false']:
                print("INFO -- KPTOP_INSECURE > allowed options are: 'true' || 'false'")
                exit(1)
        except (KeyError) as e:
            SystemExit(f"\nERROR -- ENV not found => {e}")

    
        # Optional ENVs
        try:
            GlobalAttrs.node_exporter_node_label  = os.environ['KPTOP_NODE_EXPORTER_NODE_LABEL']
        except:
            pass

        try:
            GlobalAttrs.env_insecure  = os.environ['KPTOP_INSECURE']
        except:
            pass
    
        try:
            GlobalAttrs.start_graphs_with_zero = os.environ['KPTOP_START_GRAPHS_WITH_ZERO']
        except:
            pass

        try:
            GlobalAttrs.log_dir = os.environ['KPTOP_LOGGING_DIR']
        except:
            pass

        try:
            GlobalAttrs.graphs_width = int(os.environ['KPTOP_GRAPH_WIDTH'])
        except:
            pass