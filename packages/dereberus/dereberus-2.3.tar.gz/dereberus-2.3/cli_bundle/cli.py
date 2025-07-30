import click
from tabulate import tabulate
from cli_bundle.dereberus import DereberusApi, get_credentials
from importlib.metadata import version, PackageNotFoundError
from cli_bundle.cli_help import CLI_HELP_MESSAGE
import os
from fpdf import FPDF
from pathlib import Path

PACKAGE_NAME = "dereberus"
def get_version():
    try:
      return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return "unknown"
    
@click.group(context_settings={"max_content_width": 200, "help_option_names": ["-h", "--help"]},help=CLI_HELP_MESSAGE)
@click.version_option(version=get_version(), prog_name="dereberus", message="%(prog)s - version %(version)s")
def dereberus_commands():
  pass

def read_public_key(public_key_path):
  full_path = os.path.expanduser(public_key_path)
  with open(full_path, "r") as openfile:
    public_key = openfile.read()
  return public_key

def get_valid_resource(resource=None, service=None, client=None):
  try:
    while True:
      user_api_token = get_credentials("user_api_token")
      if not resource and not service:
        user_input = click.prompt("Enter Resource or Service (format: <service> or <client|service>)")
        if "|" in user_input:
          client, service = user_input.split("|", 1)
        else:
          resource = user_input
      if service and not client:
        client = click.prompt("Enter the Client name for the service")
      if client and not service:
        client = click.prompt("Enter the Service name for the client")
      if service and client:
        data = {"service_name": service, "client_name": client}
        endpoint = "/requests/validate_service"
      else:
        data = {"resource_name": resource}
        endpoint = "/requests/resources"
      valid_response = DereberusApi.post(user_api_token, endpoint, data=data)

      if valid_response.status_code == 200:
        if endpoint == "/requests/validate_service":
          resource = valid_response.json()["resource"]
        return resource
      click.echo("Invalid input. Please try again.")
      resource, service, client = None, None, None
  except Exception as e:
      click.echo(f"Error in job execution: {e}")
      return

def format_stats(data):
    lines = []
    lines.append("📊  STATS SUMMARY")
    lines.append("-" * 40)
    lines.append(f"👤  Total Users: {data['total_users']}")
    lines.append(f"🖥️  Total Resources: {data['total_resources']}")
    lines.append(f"📄  Total Requests: {data['total_requests']}")
    accessed_resources_by_user = {}
    for accessed_resource in data['accessed_resources']:
      user = accessed_resource['username']
      if user not in accessed_resources_by_user:
        accessed_resources_by_user[user] = []
      accessed_resources_by_user[user].append(accessed_resource)
    for user, resources in accessed_resources_by_user.items():
      lines.append(f"\n👤 {user}:")
      resource_grouped = {}
      for resource in resources:
        if resource["resource_name"] not in resource_grouped:
          resource_grouped[resource["resource_name"]] = []
        resource_grouped[resource["resource_name"]].append(resource)
      for resource_name, resource_list in resource_grouped.items():
        lines.append(f"\n🖥️ {resource_name}")
        for resource in resource_list:
          lines.append(f"  - {resource['reason']} at {resource['reviewed_at']}")
      lines.append("-" * 40)
    return "\n".join(lines)
    
def to_startcase(text):
  return ' '.join(word.capitalize() for word in text.replace("_", " ").split())

def format_stats_pdf(data, output_filename="stats_report.pdf"):
    home = str(Path.home())
    output_filename = os.path.join(home, "Downloads", output_filename)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Dereberus Stats Report", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"{to_startcase('total_users')}: {data['total_users']}", ln=True)
    pdf.cell(200, 10, txt=f"{to_startcase('total_resources')}: {data['total_resources']}", ln=True)
    pdf.cell(200, 10, txt=f"{to_startcase('total_requests')}: {data['total_requests']}", ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, txt=to_startcase("accessed_resources") + ":", ln=True)
    pdf.ln(5)
    accessed_resources_by_user = {}
    for accessed_resource in data['accessed_resources']:
        user = accessed_resource['username']
        if user not in accessed_resources_by_user:
            accessed_resources_by_user[user] = []
        accessed_resources_by_user[user].append(accessed_resource)
    for user, resources in accessed_resources_by_user.items():
        pdf.cell(200, 10, txt=f"{to_startcase(user)}:", ln=True)
        resource_grouped = {}
        for resource in resources:
            resource_name = resource["resource_name"]
            if resource_name not in resource_grouped:
                resource_grouped[resource_name] = []
            resource_grouped[resource_name].append(resource)
        for resource_name, resource_list in resource_grouped.items():
            if resource_name is not None:
                pdf.cell(200, 10, txt=f" {to_startcase(resource_name)}", ln=True)
            for resource in resource_list:
                reason = to_startcase(resource['reason'])
                reviewed_at = resource['reviewed_at']
                pdf.cell(200, 10, txt=f"  - {reason} at {reviewed_at}", ln=True)
            pdf.ln(5)
    pdf.output(output_filename)
    click.echo(f"PDF generated and saved as '{output_filename}'")

@dereberus_commands.command()
def login():
  user_api_token = get_credentials("user_api_token")
  if user_api_token is None:
    click.echo("API token not found")
    return
  user_data_response = DereberusApi.get(auth_token=user_api_token, endpoint="/auth/login")
  if user_data_response.status_code != 200:
    click.echo(user_data_response.json()["message"])
    return
  click.echo(user_data_response.json()["message"])
  user_data = user_data_response.json()["user_data"]
  if user_data_response.json()["user_exist"] == False:
    try:
      public_key_path = click.prompt("Enter the path to your public key file")
      public_key = read_public_key(public_key_path)
    except Exception as e:
      click.echo(f"Error: {e}")
      return
    response = DereberusApi.post(user_api_token, "/auth/user", data={"public_key": public_key, "user_data": user_data})
    if response.status_code != 200:
      click.echo(response.json().get("message"))
      return
    click.echo(response.json().get("message"))
    return
  click.echo("Public key is already set up.")
  click.echo("Do you want to change it? (y/n)")
  choice = input()
  if choice.lower() == "n":
    return
  try:
    public_key_path = click.prompt("Enter the path to your public key file")
    public_key = read_public_key(public_key_path)
  except Exception as e:
    click.echo(f"Error: {e}")
    return
  response = DereberusApi.post(user_api_token, "/auth/user", data={"public_key": public_key})
  if response.status_code != 200:
    click.echo(response.json().get("message"))
    return
  click.echo(response.json().get("message"))
  return

@dereberus_commands.command()
@click.option("--resource", "-r", required=False, help="Resource name to request")
@click.option("--service", "-s", required=False, help="service name to request")
@click.option("--client", "-c", required=False, help="Client name for the service")
@click.option("--reason", "-m", required=False, help="Reason for requesting access")
def access( resource, service, client, reason):
  if service and not client:
    click.echo("Error: If you specify a service, you must also provide a client using -c")
    return
  if not service and client:
    click.echo("Error: If you specify a client, you must also provide a service using -s")
    return
  resource = get_valid_resource(resource, service, client)
  if not resource and not service:
    click.echo("Invalid input. Please enter a valid resource or service|client.")
    return
  if not reason:
    reason = click.prompt("Enter the Reason")
  process_request(resource, reason)

def process_request(resource, reason):
  user_api_token = get_credentials("user_api_token")
  if user_api_token is None:
    click.echo("API token not found")
    return
  resource_response = DereberusApi.post(user_api_token, "/requests/create", data={"resource_name": resource, "reason": reason})
  if resource_response.status_code != 200:
    click.echo(resource_response.json().get("message"))
    return
  click.echo(resource_response.json().get("message"))
  return
  
@dereberus_commands.command()
def resource():
  user_api_token = get_credentials("user_api_token")
  if user_api_token is None:
    click.echo("API token not found")
    return
  list_response = DereberusApi.get(user_api_token, "/resources/list")
  if list_response.status_code != 200:
    click.echo(list_response.json().get("message"))
    return
  resources = list_response.json()
  headers = ["name", "ip"]
  rows = [[req.get(header, "") for header in headers] for req in resources]
  click.echo(tabulate(rows, headers=headers, tablefmt="psql"))

@dereberus_commands.command()
@click.option("--mode","-m", type=click.Choice(["pending", "approved", "all"], case_sensitive=False), default="pending", help="Filter requests by status.")
@click.option("--days","-n", required=False, help="List the request for last N days")
def list(mode, days):
  user_api_token = get_credentials("user_api_token")
  if user_api_token is None:
    click.echo("API token not found")
    return
  list_response = DereberusApi.post(user_api_token, "/admin/list", data={"mode": mode, "days": days})
  if list_response.status_code != 200:
    try:
      click.echo(list_response.json().get("message"))
    except Exception as e:
      click.echo(f"Error in job execution: {e}")
    return
  requests = list_response.json()
  headers = ["id", "mobile", "email", "resource", "ip", "reason", "status", "approver", "created_at", "reviewed_at", "completed_at"]
  rows = [[req.get(header, "") for header in headers] for req in requests]
  click.echo(tabulate(rows, headers=headers, tablefmt="psql"))

@dereberus_commands.command()
@click.option("--request-id","-i", prompt="Enter request ID", help="ID of the request to approve")
def approve(request_id):
  user_api_token = get_credentials("user_api_token")
  if user_api_token is None:
    click.echo("API token not found")
    return
  response = DereberusApi.post(user_api_token, "/admin/approve", data={"request_id": request_id})
  if response.status_code != 200:
    try:
      click.echo(response.json().get("message"))
    except Exception as e:
      click.echo(f"Error in job execution: {e}")
    return
  click.echo(response.json().get("message"))

@dereberus_commands.command()
@click.option("--request-id","-i", prompt="Enter request ID", help="ID of the request to reject")
def reject(request_id):
  user_api_token = get_credentials("user_api_token")
  if user_api_token is None:
    click.echo("API token not found")
    return
  response = DereberusApi.post(user_api_token, "/admin/reject", data={"request_id": request_id})
  if response.status_code != 200:
    try:
      click.echo(response.json().get("message"))
    except Exception as e:
      click.echo(f"Error in job execution: {e}")
    return
  click.echo(response.json().get("message"))

@dereberus_commands.command()
@click.option("--days","-n", required=False, help="List the stats for last N days")
def stats(days):
  user_api_token = get_credentials("user_api_token")
  if user_api_token is None:
    click.echo("API token not found")
    return
  response = DereberusApi.get(user_api_token,f"/summary/stats?days={days}")
  if response.status_code != 200:
    click.echo(response.json().get("message"))
    return
  data = response.json()
  click.echo(format_stats(data))

@dereberus_commands.command()
@click.option("--days","-n", required=False, help="List the stats for last N days")
def download_stats(days):
  user_api_token = get_credentials("user_api_token")
  if user_api_token is None:
    click.echo("API token not found")
    return
  response = DereberusApi.get(user_api_token,f"/summary/stats?days={days}")
  if response.status_code != 200:
    click.echo(response.json().get("message"))
    return
  data = response.json()
  format_stats_pdf(data)

dereberus_commands.add_command(login)
dereberus_commands.add_command(access)
dereberus_commands.add_command(list)
dereberus_commands.add_command(approve)
dereberus_commands.add_command(reject)
dereberus_commands.add_command(resource)
dereberus_commands.add_command(stats)
dereberus_commands.add_command(download_stats)

if __name__ == "__main__":
    dereberus_commands()
