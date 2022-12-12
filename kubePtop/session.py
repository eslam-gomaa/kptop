import requests
import json
# import urllib3
# import socket
from urllib3.exceptions import InsecureRequestWarning
import rich
# from rich.markdown import Markdown
from kubePtop.global_attrs import GlobalAttrs
from kubePtop.logging import Logging
logging = Logging()
# Ignore Warning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
# https://stackoverflow.com/a/41041028
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'

class PrometheusAPI:

    def __init__(self):
        self.verify = False
        self.session = None
        self.prometheus_url = GlobalAttrs.env_prometheus_server
        self.prometheus_url_query = self.prometheus_url + "/api/v1/query"

    def get_session(self):
        try:
            session = requests.Session()
            Logging.log.info("Establishing a new connection with Prometheus")
            self.session = session
            session.verify = self.verify
            prometheus_url = self.prometheus_url + "/-/healthy"
            if GlobalAttrs.debug:
                print(f"DEBUG -- Connecting to Prometheus: {prometheus_url}")
            Logging.log.info(f"Connecting to Prometheus: {prometheus_url}")
            req = session.get(prometheus_url)
            if req.status_code == 200:
                Logging.log.info(f"connected successfully, status_code: {req.status_code}")
                if GlobalAttrs.debug:
                    print(f"DEBUG -- connected successfully, status_code: {req.status_code}")
                    print(f"DEBUG -- Response: \n{req.text}")
            else:
                print(f"ERROR -- Failed to connect to Prometheus '{GlobalAttrs.env_prometheus_server}'; status_code: {req.status_code}, reason: {req.reason}\n")
                Logging.log.error(f"Failed to connect to Prometheus, status_code: {req.status_code}")
                if GlobalAttrs.debug:
                    Logging.log.debug("Exiting.")
                exit(1)
        except requests.exceptions.Timeout as e:
            print(f"ERROR -- Failed to connect to Prometheus '{GlobalAttrs.env_prometheus_server}'; Timeout\n")
            Logging.log.error(f"Failed to connect to Prometheus '{GlobalAttrs.env_prometheus_server}'; Timeout\n")
            Logging.log.error(e)
            raise SystemExit(f"> {e}")
        except requests.exceptions.TooManyRedirects:
            print(f"ERROR -- Failed to connect to Prometheus '{GlobalAttrs.env_prometheus_server}'; Too Many Redirects\n")
            Logging.log.error(f"Failed to connect to Prometheus '{GlobalAttrs.env_prometheus_server}'; Too Many Redirects\n")
            Logging.log.error(e)
            raise SystemExit(f"> {e}")
        except Exception as e:
            print(f"ERROR -- Failed to connect to Prometheus '{GlobalAttrs.env_prometheus_server}'; Connection Failed\n")
            Logging.log.error(f"Failed to connect to Prometheus '{GlobalAttrs.env_prometheus_server}'; Connection Failed\n")
            Logging.log.error(e)
            raise SystemExit(f"> {e}")

    def verify_prometheus_connection(self):
        out = {
            "connected": False,
            "status_code": "?",
            "reason": "",
            "fail_reason": ""
        }
        session = requests.Session()
        session.verify = self.verify
        try:
            if GlobalAttrs.debug:
                print("DEBUG -- Checking Prometheus existing connection")
            Logging.log.info("Checking Prometheus existing connection")
            prometheus_url = self.prometheus_url + "/-/healthy"
            if GlobalAttrs.debug:
                print(f"DEBUG -- Connecting to Prometheus: {prometheus_url}")
            req = session.get(self.prometheus_url + "/-/healthy")
            if req.status_code == 200:
                Logging.log.info(f"connected successfully, status_code: {req.status_code}")
                if GlobalAttrs.debug:
                    print(f"DEBUG -- connected successfully, status_code: {req.status_code}")
                out["connected"] = True
                out["status_code"] = req.status_code
            else:
                out["status_code"] = req.status_code
                out["reason"] = req.reason
                out["fail_reason"] = f"Failed to connect to Prometheus. Reason: {req.reason}"
                Logging.log.error(f"Failed to connect to Prometheus. Reason: {req.reason}")
        except Exception as e:
            out["fail_reason"] = f"Failed to connect to Prometheus; {e}"
            out["reason"] = "unable to connnect"
            Logging.log.info(f"Failed to connect to Prometheus; {e}")

        return out

    def run_query(self, query):
        if self.session is None:
            if GlobalAttrs.debug:
                Logging.log.debug(f"While running a query .. establishing a new connection with Prometheus.")
                print(f"DEBUG -- While running a query .. establishing a new connection with Prometheus.")
            self.get_session()
        try:
            Logging.log.info(f"Running Query:\n\t\t  => {query}")
            req = self.session.get(self.prometheus_url_query, params={'query': f'{query}'})
            if req.status_code == 200:
                Logging.log.info(f"Query run successfully, exit_code: {req.status_code}; Result:\n{json.loads(req.text)}")
                return json.loads(req.text)
            else:
                Logging.log.error(f"Query did NOT run successfully, exit_code: {req.status_code}")
                return {}
        except requests.exceptions.Timeout as e:
            print(f"ERROR -- Failed to connect to Prometheus: Timeout\n")
            Logging.log.error(f"Query did NOT run successfully, {e}")
            raise SystemExit(f"> {e}")
        except requests.exceptions.TooManyRedirects:
            print(f"ERROR -- Failed to connect to Prometheus: Too Many Redirects \n")
            Logging.log.error(f"Query did NOT run successfully, {e}")
            raise SystemExit(f"> {e}")
        except (requests.exceptions.RequestException) as e:
            print(f"ERROR -- Failed to connect to Prometheus: Connection Failed\n")
            Logging.log.error(f"Query did NOT run successfully, {e}")
            raise SystemExit(f"> {e}")
            
    def verifyNodeExporter(self):
        """
        not in use at the moment
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": {}
        }
        try:
            query = 'sum(node_exporter_build_info) by (version)'
            result = self.run_query(query)
            if not result.get('status') == 'success':
                output['fail_reason'] = f"could not get metric value:\n {query}"
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data:\n {query}"
                return output
                
            found_versions= {}
            for v in result.get('data').get('result'):
                found_versions[v.get('metric').get('version')] = v.get('value')[1]
            output['result']['found_versions'] = found_versions
            output['success'] = True

        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e

        return output

    def verifyKubernetesExporter(self):
        """
        not in use at the moment
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": {}
        }
        try:
            query = 'sum(kubernetes_build_info) by (git_version)'
            result = self.run_query(query)
            if not result.get('status') == 'success':
                output['fail_reason'] = f"could not get metric value:\n {query}"
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data:\n {query}"
                return output
                
            found_versions= {}
            for v in result.get('data').get('result'):
                found_versions[v.get('metric').get('git_version')] = v.get('value')[1]
            output['result']['found_git_versions'] = found_versions
            output['success'] = True

        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e

        return output

    def verify_exporters(self):
        
        # Verify node_exporter
        # Check build info
        # Needed results
        # - avaialable not not
        # - version

        print("")        
        rich.print("[underline]Verifying Prometheus connection:[/underline] ...                    ", end="\r")
        prometheus_connection = self.verify_prometheus_connection()
        if prometheus_connection['connected']:
            rich.print("[underline]Verifying Prometheus connection:[/underline] [bold green]Connected                     ")
            rich.print_json(data=prometheus_connection)
        else:
            rich.print("[underline]Verifying Prometheus connection:[/underline] [bold red]Unable to connect                     ")
            rich.print_json(data=prometheus_connection)
            exit(1)
        
        print("")
        rich.print("[underline]Verifying Prometheus Exporters:[/underline]")
        print("")
        rich.print("* Node Exporter:  ...               ", end="\r")
        verify_node_exporter = self.verifyNodeExporter()
        if verify_node_exporter.get('success'):
            rich.print("* Node Exporter:  [bold green]Found           ", end="\r")
        else:
            rich.print("* Node Exporter:  [bold red]Not Found           ", end="\r")
        print("")
        rich.print_json(data=verify_node_exporter)
        print("")
        rich.print("* Kubernetes Exporter: ...         ", end="\r")
        verify_kubernetes_exporter = self.verifyKubernetesExporter()
        if verify_kubernetes_exporter.get('success'):
            rich.print("* Kubernetes Exporter:  [bold green]Found           ", end="\r")
        else:
            rich.print("* Kubernetes Exporter:  [bold green]Not Found           ", end="\r")
        print("")
        rich.print_json(data=verify_kubernetes_exporter)
        print(" ")



