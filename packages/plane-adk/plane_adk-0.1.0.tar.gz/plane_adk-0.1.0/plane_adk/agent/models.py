from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


### Plane Webhook Models
class Credentials(BaseModel):
    client_id: str
    client_secret: str
    app_installation_id: str
    base_url: Optional[str] = "https://api.plane.so"
    redirect_uri: str


class Actor(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    avatar: str
    avatar_url: Optional[str]
    display_name: str


class Activity(BaseModel):
    field: Optional[str] = None
    new_value: Optional[Any]
    old_value: Optional[Any]
    actor: Actor
    old_identifier: Optional[Any]
    new_identifier: Optional[Any]


class OAuthResponse(BaseModel):
    access_token: str
    expires_in: int
    token_type: str
    scope: str
    app_installation_id: str
    workspace_id: str
    bot_user_id: str
    workspace_slug: str


class EventData(BaseModel):
    """Base model for webhook event data with common fields"""

    model_config = ConfigDict(extra="allow")  # Allow additional fields

    id: str
    project: Optional[str] = None  # Some events might not have project
    workspace: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class IssueEventData(EventData):
    """Specific model for issue events"""

    name: Optional[str] = None
    description_html: Optional[str] = None
    priority: Optional[str] = None
    assignees: Optional[list] = None
    labels: Optional[list] = None
    state: Optional[dict] = None


class CommentEventData(EventData):
    """Specific model for comment events"""

    issue: Optional[str] = None  # For comment events, this refers to the issue ID
    comment_html: Optional[str] = None
    comment_stripped: Optional[str] = None


class WebhookEvent(BaseModel):
    event: str
    action: str
    webhook_id: str
    workspace_id: str
    data: Any
    activity: Activity


### Agent Models
class Context(BaseModel):
    entity_name: str
    entity_id: str
    issue_id: str
    event: WebhookEvent
    workspace_slug: str
    workspace_id: str
    project_id: Optional[str] = None
    issue_payload: Optional[dict] = None


class TokenDetails(BaseModel):
    access_token: str
    expires_in: int
    token_type: str
    scope: str


class WorkspaceDetails(BaseModel):
    slug: str
    id: str
    bot_user_id: str
