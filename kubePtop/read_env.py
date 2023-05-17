import os
from kubePtop.global_attrs import GlobalAttrs

class ReadEnv:
    def __init__(self):
        pass
    
    def check_env(self, envs):
        """Checks if the ENV is defined

        Args:
            env (lst): takes a list of ENVs
        Return: dct
        """
        output = {
            "missing": False,
            "missing_envs": []
        }
        for env in envs:
            try:
                os.environ[f'{env}']
            except KeyError as e:
                output['missing'] = True
                output['missing_envs'].append(env)
        return output
        

    def read_env(self):
        """
        Read Environment variables
        """
        # Mandatory ENVs
        # try:
        #     GlobalAttrs.env_prometheus_server  = os.environ['KPTOP_PROMETHEUS_SERVER']
        # except (KeyError) as e:
        #     raise SystemExit(f"\nERROR -- ENV not found => {e}")

        # Basic Auth ENVs
        
        # Default to "pod_portForward" if the ENV is not set.
        check_conn_method = self.check_env(['KPTOP_CONNECTION_METHOD'])
        if check_conn_method['missing']:
            print(f"INFO -- ENV: {check_conn_method.get('missing_envs')} is missing\n")
            print('github link')            
            exit(1)
        try:
            os.environ['KPTOP_CONNECTION_METHOD']
        except KeyError:
                os.environ['KPTOP_CONNECTION_METHOD'] = "pod_portForward"
        
        try:    
            if os.environ['KPTOP_CONNECTION_METHOD'] == "pod_portForward":
                GlobalAttrs.env_connection_method = os.environ['KPTOP_CONNECTION_METHOD']
                
                check = self.check_env(['KPTOP_PROMETHEUS_POD_NAME', 'KPTOP_PROMETHEUS_POD_PORT', 'KPTOP_PROMETHEUS_POD_NAMESPACE'])
                if check['missing']:
                    print(f"INFO -- ENVs: {check.get('missing_envs')} are missing")
                    exit(1)
                    
                GlobalAttrs.env_prometheus_pod_name = os.environ['KPTOP_PROMETHEUS_POD_NAME']
                GlobalAttrs.env_prometheus_pod_port = os.environ['KPTOP_PROMETHEUS_POD_PORT']
                GlobalAttrs.env_prometheus_pod_namespace = os.environ['KPTOP_PROMETHEUS_POD_NAMESPACE']
                

            if os.environ['KPTOP_CONNECTION_METHOD'] == "prometheus_endpoint":
                GlobalAttrs.env_connection_method = os.environ['KPTOP_CONNECTION_METHOD']
                
                check = self.check_env(['KPTOP_PROMETHEUS_SERVER'])
                if check['missing']:
                    print(f"INFO -- ENVs: {check.get('missing_envs')} are missing")
                    exit(1)
                GlobalAttrs.env_prometheus_server  = os.environ['KPTOP_PROMETHEUS_SERVER']
                
                if os.environ['KPTOP_BASIC_AUTH_ENABLED']:
                    check = self.check_env(['KPTOP_PROMETHEUS_USERNAME', 'KPTOP_PROMETHEUS_PASSWORD'])
                    if check['missing']:
                        print(f"INFO -- ENVs: {check.get('missing_envs')} are missing")
                        exit(1)
                    GlobalAttrs.env_basic_auth_enabled   = os.environ['KPTOP_BASIC_AUTH_ENABLED']
                    GlobalAttrs.env_prometheus_username  = os.environ['KPTOP_PROMETHEUS_USERNAME']
                    GlobalAttrs.env_prometheus_password  = os.environ['KPTOP_PROMETHEUS_PASSWORD']

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
            GlobalAttrs.env_kube_config_file  = os.environ['KUBECONFIG']
        except:
            pass
        
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