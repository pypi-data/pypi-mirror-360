import subprocess
import requests
from requests.auth import HTTPBasicAuth
import yaml
from griddot.tools.utils import get_container_command


def helm_list_charts():
    encoded_project = requests.utils.quote("griddot/packages", safe="")
    url = f"https://gitlab.com/api/v4/projects/{encoded_project}/packages/helm/stable/index.yaml"

    # GitLab expects: username = anything (often 'gitlab-ci-token'), password = the token
    auth = HTTPBasicAuth("helm-user", "glpat-mKckaB2sg2vC74xzFWWB")  # or "gitlab-ci-token", token

    response = requests.get(url, auth=auth)
    response.raise_for_status()

    index = yaml.safe_load(response.text)
    charts = list(index.get("entries", {}).keys())
    charts = [f"griddot/{chart}" for chart in charts]
    return charts


def helm_template(deployment: str, values: tuple[str] = None):
    """
    Create a Kubernetes deployment using helm, from the possible deployments in list_helm_charts.
    """
    container_cmd = get_container_command()
    if len(values) > 0:
        values_mount = " ".join([f"-v ./{value}:/{value.split('/')[-1]}" for value in values])
        values_option = "".join([f"-f /{value.split('/')[-1]} " for value in values])
    else:
        values_option = ""
        values_mount = ""

    result = subprocess.run(
        f"{container_cmd} run --rm {values_mount} registry.gitlab.com/griddot/packages/helm:latest helm template {deployment} {values_option}",
        shell=True, check=True, capture_output=True
    )

    return result.stdout.decode('utf-8')
