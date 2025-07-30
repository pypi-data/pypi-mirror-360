from plane.api_client import ApiClient
from plane.configuration import Configuration
from plane.oauth.api import OAuthApi

from plane_adk.agent.handlers import AgentEventHandler, IssueEventHandler
from plane_adk.agent.models import Credentials, TokenDetails, WorkspaceDetails


class PlaneAgent:
    issue: AgentEventHandler
    token_details: TokenDetails
    workspace_details: WorkspaceDetails

    def __init__(self, credentials: Credentials):
        self.credentials = credentials
        self._init_token()
        configuration = Configuration(
            host=credentials.base_url,
            access_token=self.token_details.access_token,
        )
        api_client = ApiClient(configuration)
        self.issue = IssueEventHandler(api_client, self.workspace_details)

    def process_webhook(self, webhook: dict):
        if webhook["event"] in ["issue", "issue_comment"]:
            self.issue.process_webhook(webhook)

    def _init_token(self):
        oauth_api = OAuthApi(
            client_id=self.credentials.client_id,
            client_secret=self.credentials.client_secret,
            redirect_uri=self.credentials.redirect_uri,
            base_url=self.credentials.base_url,
        )
        token_response = oauth_api.get_bot_token(self.credentials.app_installation_id)
        self.token_details = TokenDetails(
            access_token=token_response.access_token,
            expires_in=token_response.expires_in,
            token_type=token_response.token_type,
            scope=token_response.scope,
        )
        app_installation = oauth_api.get_app_installation(
            self.token_details.access_token, self.credentials.app_installation_id
        )
        self.workspace_details = WorkspaceDetails(
            slug=app_installation.workspace_detail.slug,
            id=app_installation.workspace,
            bot_user_id=app_installation.app_bot,
        )
