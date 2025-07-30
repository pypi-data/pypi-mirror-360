from abc import ABC, abstractmethod
from typing import Callable

from plane.api.work_item_comments_api import WorkItemCommentsApi
from plane.api.work_items_api import WorkItemsApi
from plane.api_client import ApiClient
from plane.models.issue_comment_create_request import IssueCommentCreateRequest

from plane_adk.agent.models import (
    Context,
    WebhookEvent,
    WorkspaceDetails,
    IssueEventData,
    CommentEventData,
)


class AgentEventHandler(ABC):
    supported_events: list[str] = []
    callbacks: dict[str, Callable] = {}

    def __init__(self, plane_client: ApiClient, workspace_details: WorkspaceDetails):
        self.plane_client = plane_client
        self.workspace_details = workspace_details

    def on(self, event_name: str, callback: Callable):
        if event_name not in self.supported_events:
            raise ValueError(f"Event {event_name} is not supported")
        self.callbacks[event_name] = callback

    @abstractmethod
    def process_webhook(self, event: dict):
        pass

    @abstractmethod
    def progress(self, message: str):
        pass

    def get_client(self) -> ApiClient:
        return self.plane_client


class IssueEventHandler(AgentEventHandler):
    supported_events: list[str] = ["assigned", "mentioned", "unassigned"]
    context: Context = None

    def process_webhook(self, event: dict):
        event_model = WebhookEvent(**event)
        if event_model.event == "issue":
            self._process_issue(event_model)
        elif event_model.event == "issue_comment":
            self._process_issue_comment(event_model)

    def _process_issue(self, event_model: WebhookEvent):
        event_data = IssueEventData(**event_model.data)
        self.context = Context(
            issue_id=event_data.id,
            event=event_model,
            workspace_id=event_model.workspace_id,
            workspace_slug=self.workspace_details.slug,
            project_id=event_data.project,
            entity_name="issue",
            entity_id=event_data.id,
            issue_payload=WorkItemsApi(self.plane_client).retrieve_work_item(
                event_data.id,
                event_data.project,
                self.workspace_details.slug,
            ),
        )

        if event_model.activity.field == "assignees":
            if (
                event_model.activity.new_identifier
                == self.workspace_details.bot_user_id
            ):
                if self.callbacks["assigned"]:
                    self.callbacks["assigned"](self, self.context)

    def _process_issue_comment(self, event_model: WebhookEvent):
        event_data = CommentEventData(**event_model.data)
        self.context = Context(
            issue_id=event_data.issue,
            event=event_model,
            workspace_id=event_model.workspace_id,
            workspace_slug=self.workspace_details.slug,
            project_id=event_data.project,
            entity_name="comment",
            entity_id=event_data.id,
            issue_payload=WorkItemsApi(self.plane_client).retrieve_work_item(
                event_data.issue,
                event_data.project,
                self.workspace_details.slug,
            ),
        )
        bot_mention = f'"{self.workspace_details.bot_user_id}"'

        if not event_model.activity:
            return

        if event_model.activity.field == "description" and (
            bot_mention in event_model.activity.new_value
            and (
                event_model.activity.old_value is None
                or bot_mention not in event_model.activity.old_value
            )
        ):
            if self.callbacks["mentioned"]:
                self.callbacks["mentioned"](self, self.context)

    def progress(self, message: str):
        WorkItemCommentsApi(self.plane_client).create_work_item_comment(
            self.context.issue_id,
            self.context.project_id,
            self.context.workspace_slug,
            IssueCommentCreateRequest(comment_html=f"<p>{message}</p>"),
        )
