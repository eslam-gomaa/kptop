import os
from kubePtop.global_attrs import GlobalAttrs

class ReadEnv:
    def __init__(self):
        self.read_env()

    def read_env(self):
        """
        Read Environment variables
        """

        # Mandatory ENV
        try:
            GlobalAttrs.env_prometheus_server  = os.environ['KUBE_PTOP_PROMETHEUS_SERVER']
        except (KeyError) as e:
            raise SystemExit(f"\nERROR -- ENV not found => {e}")

        # Optional ENV
        try:
            GlobalAttrs.env_basic_auth_enabled  = os.environ['KUBE_PTOP_BASIC_AUTH_ENABLED']
            GlobalAttrs.env_prometheus_username  = os.environ['KUBE_PTOP_PROMETHEUS_USERNAME']
            GlobalAttrs.env_prometheus_password  = os.environ['KUBE_PTOP_PROMETHEUS_PASSWORD']
            GlobalAttrs.env_insecure  = os.environ['KUBE_PTOP_INSECURE']
        except (KeyError) as e:
            pass

        if GlobalAttrs.env_basic_auth_enabled not in [True, False, 'true', 'false']:
            print("INFO -- KUBE_PTOP_BASIC_AUTH_ENABLED > allowed options are: 'true' || 'false'")
            exit(1)

        if GlobalAttrs.env_insecure not in [True, False, 'true', 'false']:
            print("INFO -- KUBE_PTOP_INSECURE > allowed options are: 'true' || 'false'")
            exit(1)


        if GlobalAttrs.env_basic_auth_enabled:
            if (GlobalAttrs.env_prometheus_username is None or GlobalAttrs.env_prometheus_password is None):
                raise SystemExit("INFO -- ENV: KUBE_PTOP_PROMETHEUS_USERNAME or KUBE_PTOP_PROMETHEUS_PASSWORD is missing")
