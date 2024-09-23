#! /usr/bin/env python3

# Modal has a concept of workspaces and each account has a default workspace and its name is same as the username
# Upon examining the web-ui I was able to find a rought workflow.

# Login with oauth callback using github 
# Button hyperlink: https://modal.com/api/login?next=%2Fhome&aId=98ed6cea-997c-4b4f-8bab-6678b82cca71
# Github OAuth URL looks like this after clicking the login button:
# https://github.com/login/oauth/authorize?
#   response_type=code
#   &client_id=53fe4b1ca04488e048e9
#   &scope=user%3Aemail
#   &state=eyJuZXh0X3BhdGgiOiAiL2hvbWUiLCAiYXV0aF9wdXJwb3NlIjogImxvZ2luIiwgImNzcmZfdG9rZW4iOiAiTjUyRTF0T2RnTXVoQlNmSjFKbndqUXlrUFhxd1BFIiwgImlkZW50aXR5X3Byb3ZpZGVyX3R5cGUiOiAxLCAiaW52aXRlX3Rva2VuIjogbnVsbCwgInNoYXJlYWJsZV90b2tlbiI6IGZhbHNlLCAidXRtX3NvdXJjZSI6IG51bGwsICJhbm9ueW1vdXNfaWQiOiAiOThlZDZjZWEtOTk3Yy00YjRmLThiYWItNjY3OGI4MmNjYTcxIiwgIndvcmtzcGFjZV91c2VybmFtZSI6IG51bGx9

# On success we will get a 302 redirect to a callback url to modal
# The callback url looks like this:
# https://modal.com/api/oauth-callback?
#   code=32c6cd10bfead661ccdc
#   &state=eyJuZXh0X3BhdGgiOiAiL2hvbWUiLCAiYXV0aF9wdXJwb3NlIjogImxvZ2luIiwgImNzcmZfdG9rZW4iOiAiTjUyRTF0T2RnTXVoQlNmSjFKbndqUXlrUFhxd1BFIiwgImlkZW50aXR5X3Byb3ZpZGVyX3R5cGUiOiAxLCAiaW52aXRlX3Rva2VuIjogbnVsbCwgInNoYXJlYWJsZV90b2tlbiI6IGZhbHNlLCAidXRtX3NvdXJjZSI6IG51bGwsICJhbm9ueW1vdXNfaWQiOiAiOThlZDZjZWEtOTk3Yy00YjRmLThiYWItNjY3OGI4MmNjYTcxIiwgIndvcmtzcGFjZV91c2VybmFtZSI6IG51bGx9

# This request would also set a cookie with the name of `modal-session` on the workspaces endpoint.

# curl 'https://modal.com/api/user/workspaces' 
#   -H 'accept: application/json' 
#   -H 'cookie: modal-session=se-1EptMwDxTOqZjsnJmSUYCo:xx-ERfkcf4DsfqHyiNdiG0DVl' 

# Response:
# [{"workspaceId":"ac-oSIfCCo6QdfLVUtW28QeFP","memberId":"me-TiCwGk1M9P2nVYRuH8vmFv","username":"djraval","isPersonal":true,"memberRole":"MEMBER_ROLE_OWNER","avatarUrl":"https://avatars.githubusercontent.com/u/20377686?v=4","environmentNames":["main"],"maxWorkspaceSeats":3,"customDomainsEnabled":false,"auditLogsEnabled":false,"oktaSsoEnabled":false,"oktaSsoEnforced":false,"stripeSubscriptionId":"","stripePaymentMethodId":"","cycleUsage":0.0,"cycleCredits":0.0,"cycleSpendLimit":0.0,"cycleCapDollars":0.0,"featureFlags":{},"cpuRegionSelectionEnabled":false,"regionSelectionEnabled":false,"planType":"PLAN_STARTER","slackTeamId":""}]
import asyncio
from modal.config import _lookup_workspace

async def get_workspace_details(server_url, token_id, token_secret):
    try:
        response = await _lookup_workspace(server_url, token_id, token_secret)
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    server_url = "https://api.modal.com"
    token_id = "ak-xxx"
    token_secret = "as-xxx"

    loop = asyncio.get_event_loop()
    workspace_details = loop.run_until_complete(get_workspace_details(server_url, token_id, token_secret))
    if workspace_details:
        print(workspace_details)