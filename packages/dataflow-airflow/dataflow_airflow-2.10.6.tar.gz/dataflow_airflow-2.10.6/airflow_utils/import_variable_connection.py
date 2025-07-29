from airflow.secrets import BaseSecretsBackend
from airflow.utils.log.logging_mixin import LoggingMixin
import boto3, os, json , requests, configparser
from airflow.providers.amazon.aws.secrets.secrets_manager import SecretsManagerBackend

class AirflowConnectionsAndVariableImport(SecretsManagerBackend):
    """
    A class to interact with AWS Secrets Manager for retrieving secrets.

    Attributes:
        client: The Boto3 client for Secrets Manager.
    """
    def __init__(self, **kwargs):
        super().__init__()
        self.config = configparser.ConfigParser()
        self.client = boto3.client('secretsmanager')
        self.user_name = os.environ["HOSTNAME"].replace("jupyter-","") if os.environ["HOSTNAME"].startswith("jupyter-") else os.environ["HOSTNAME"]

    def _get_secret(self, vault_path):
        """
        Fetches the secret for a connection ID.

        Args:
            conn_id (str): Connection ID.
        Returns:
            str: Secret string or `None` if not found.
        """
        secret_id = vault_path
        response = self.client.get_secret_value(SecretId=secret_id)
        if (response and json.loads(response.get("SecretString"))):
            return response.get("SecretString")
        else:
            return None

    def get_conn_value(self, conn_id):
        """
        Get serialized representation of Connection.

        :param conn_id: connection id
        """
        try:
            runtime = os.environ.get("RUNTIME")
            slug = os.environ.get("SLUG")

            if runtime and slug:
                vault_path = f"{runtime}/{slug}/connections/{conn_id}"
            else:
                vault_path = f"{self.user_name}/connections/{conn_id}"

            connection = self._get_secret(vault_path)
            if connection is None:
                raise Exception(f"Connection {conn_id} not found.")
            
            if connection is not None and connection.strip().startswith("{"):
                connection_dict = json.loads(connection)
                connection_dict['schema'] = connection_dict.pop('schemas')
                connection_dict.pop('conn_id')
                if connection_dict['conn_type'] == "PostgreSQL":
                    connection_dict['conn_type'] = "postgres"
                standardized_connection_dict = self._standardize_secret_keys(connection_dict)
                if self.are_secret_values_urlencoded:
                    standardized_connection_dict = self._remove_escaping_in_secret_dict(standardized_connection_dict)
                standardized_connection = json.dumps(standardized_connection_dict)
                return standardized_connection
            else:
                return connection
        except Exception as e:
            raise Exception(f"Error retrieving connection: {e}")

    def get_variable(self, key):
        """
        Get Airflow Variable.

        :param key: Variable Key
        :return: Variable Value
        """
        try:
            runtime = os.environ.get("RUNTIME")
            slug = os.environ.get("SLUG")

            self.config.read('/dataflow/app/auth_config/dataflow_auth.cfg')
            variableorsecret_api = self.config.get('auth', 'db_get_variableorsecret')
            
            if not variableorsecret_api:
                print("[Dataflow.variable] Variable Unreachable")
                return None
            
            query_params = {
                "key": key,
                "created_by": self.user_name,
                "runtime": runtime,
                "slug": slug
            }
            
            response = requests.get(variableorsecret_api, params=query_params)
            
            if response.status_code == 200:
                response_text = response.text.strip().strip('"')
                return response_text
            
        except Exception as e:
            print(f"Exception occurred: {e}")
            return None