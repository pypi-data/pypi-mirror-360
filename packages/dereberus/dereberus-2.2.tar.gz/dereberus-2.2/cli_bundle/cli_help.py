CLI_HELP_MESSAGE = """
\033[1;36mDereberus CLI  -  Manage Resource Access & Admin Actions\033[0m

\033[1mUSAGE:\033[0m\n\n
  \033[92mdereberus [COMMAND] [OPTIONS]\033[0m

\033[1mAVAILABLE COMMANDS EXAMPLES:\033[0m\n\n
  \033[92mdereberus login\033[0m - Authenticate yourself with Dereberus and set up your public key.\n
  \033[92mdereberus resource\033[0m - Show a table of all resources (name & IP) you may request access to.\n
  \033[92mdereberus access\033[0m - Request access to a resource or to a specific service/client.\n
  \033[92mdereberus access -r "proboscis" -m "Debugging"\033[0m - For resource access, use -r and -m to specify the resource and your reason.\n
  \033[92mdereberus access -s "b" -c "dailyneeds" -m "Maintenance"\033[0m - For service/client access, use both -s and -c with -m to specify the service/client and your reason.\n
  \033[92mdereberus list\033[0m - List access requests with filters (default shows pending requests).\n
  \033[92mdereberus list -m all\033[0m - Show all access requests (admin only).\n
  \033[92mdereberus list -m approved\033[0m - Show only approved access requests.\n
  \033[92mdereberus list -m all -n 3\033[0m - Limit the list to requests from the last N days using -n.\n
  \033[92mdereberus approve\033[0m - Approve a specific access request (admin only).\n
  \033[92mdereberus approve -i 42\033[0m - Approve an access request by specifying its request ID.\n
  \033[92mdereberus reject\033[0m - Reject a specific access request (admin only).\n
  \033[92mdereberus reject -i 43\033[0m - Reject an access request by specifying its request ID.\n
  \033[92mdereberus stats\033[0m - Get stats for the last N days (default is 3 days).\n
  \033[92mdereberus stats -n 3\033[0m - Limit the stats to requests from the last N days using -n.\n
  \033[92mdereberus download_stats\033[0m - Download stats for the last N days (default is 3 days).\n
  \033[92mdereberus download_stats -n 3\033[0m - Limit the stats to requests from the last N days using -n.\n
\033[1mTIP:\033[0m
  Use '\033[92mdereberus <command> --help\033[0m' to view details for each command.
"""