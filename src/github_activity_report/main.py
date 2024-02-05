import datetime
import json
import os
import re
from pathlib import Path
from typing import NamedTuple, TypeGuard

import requests
from pydantic import ValidationError

from github_activity_report import github_models

USERNAME = os.getenv("GAR_USERNAME", "benoit74")
GITHUB_TOKEN = os.getenv("GAR_GITHUB_TOKEN", None)
START_DATETIME = datetime.datetime.fromisoformat("2024-01-29T17:00:00Z")


def get_resp_header(result: requests.Response, header: str) -> str:
    value = result.headers.get(header)
    assert value
    return value


LINK_PATTERN = re.compile(r'<(?P<url>.+?)>; rel="(?P<rel>.+?)"')
INITIAL_EVENTS_PATH = Path("output/initial_events.json")

ISSUE_PR_LINK_PATTERN = re.compile(
    r"(?:close(?:s|d)?|fix(?:es|ed)?|resolve(?:s|d)?)\s+#(?P<id>\d+)", re.IGNORECASE
)


def get_all_initial_events():
    all_events = []
    cur_link = "https://api.github.com/users/benoit74/events?per_page=100"
    while True:
        response = requests.get(
            cur_link,
            headers={
                "Accept": "application/vnd.github+json",
                "X-Github-Api-Version": "2022-11-28",
                "Authorization": f"Bearer {GITHUB_TOKEN}",
            },
        )
        response.raise_for_status()
        etag = get_resp_header(response, "etag")
        link = get_resp_header(response, "link")
        next_link = None
        last_link = None
        for match in re.finditer(LINK_PATTERN, link):
            if match.group("rel") == "next":
                next_link = match.group("url")
            if match.group("rel") == "last":
                last_link = match.group("url")
        poll_interval = get_resp_header(response, "x-poll-interval")
        ratelimit_remaining = get_resp_header(response, "x-ratelimit-remaining")
        ratelimit_used = get_resp_header(response, "x-ratelimit-used")
        ratelimit_limit = get_resp_header(response, "x-ratelimit-limit")
        ratelimit_reset = datetime.datetime.fromtimestamp(
            float(get_resp_header(response, "x-ratelimit-reset")),
            tz=datetime.UTC,
        )
        events = response.json()
        all_events.extend(events)  # pyright: ignore [reportUnknownMemberType]
        print(f"{len(events)} events found")
        print(f"Etag: {etag}")
        print(f"Poll interval: {poll_interval}")
        print(f"Link: {link}")
        print(
            f"Rate limit: {ratelimit_used} used out of {ratelimit_limit}, {ratelimit_remaining} remains, reset is at {ratelimit_reset} UTC"
        )
        if not next_link or not last_link or cur_link == last_link:
            break
        cur_link = next_link

    print(
        f"Total: {len(all_events)} events found"  # pyright: ignore [reportUnknownArgumentType]
    )
    with open(INITIAL_EVENTS_PATH, "w") as fh:
        json.dump(all_events, fh)


def load_events() -> list[github_models.Event]:
    events_raw = json.loads(INITIAL_EVENTS_PATH.read_text())
    try:
        events_obj = github_models.Events.model_validate(events_raw)
        return events_obj.root
    except ValidationError as ex:
        print("WARNING, failed to deserialize the whole payload, fallbacking")
        print(ex)

    events_list: list[github_models.Event] = []
    for event_raw in events_raw:
        # first deserialize the light version to have access to the type
        try:
            event_light = github_models.EventLight.model_validate(event_raw)
        except ValidationError as ex:
            print("Error, failed to deserialize the event which won't be processed")
            print(json.dumps(event_raw, indent=True))
            print(ex)
            continue

        try:
            if event_light.type == "CommitCommentEvent":
                event_obj = github_models.CommitCommentEvent.model_validate(event_raw)
            elif event_light.type == "CreateEvent":
                event_obj = github_models.CreateEvent.model_validate(event_raw)
            elif event_light.type == "DeleteEvent":
                event_obj = github_models.DeleteEvent.model_validate(event_raw)
            elif event_light.type == "ForkEvent":
                event_obj = github_models.ForkEvent.model_validate(event_raw)
            elif event_light.type == "GollumEvent":
                event_obj = github_models.GollumEvent.model_validate(event_raw)
            elif event_light.type == "IssueCommentEvent":
                event_obj = github_models.IssueCommentEvent.model_validate(event_raw)
            elif event_light.type == "IssuesEvent":
                event_obj = github_models.IssuesEvent.model_validate(event_raw)
            elif event_light.type == "MemberEvent":
                event_obj = github_models.MemberEvent.model_validate(event_raw)
            elif event_light.type == "PublicEvent":
                event_obj = github_models.PublicEvent.model_validate(event_raw)
            elif event_light.type == "PullRequestEvent":
                event_obj = github_models.PullRequestEvent.model_validate(event_raw)
            elif event_light.type == "PullRequestReviewEvent":
                event_obj = github_models.PullRequestReviewEvent.model_validate(
                    event_raw
                )
            elif event_light.type == "PullRequestReviewCommentEvent":
                event_obj = github_models.PullRequestReviewCommentEvent.model_validate(
                    event_raw
                )
            elif event_light.type == "PullRequestReviewThreadEvent":
                event_obj = github_models.PullRequestReviewThreadEvent.model_validate(
                    event_raw
                )
            elif event_light.type == "PushEvent":
                event_obj = github_models.PushEvent.model_validate(event_raw)
            elif event_light.type == "ReleaseEvent":
                event_obj = github_models.ReleaseEvent.model_validate(event_raw)
            elif event_light.type == "SponsorshipEvent":
                event_obj = github_models.SponsorshipEvent.model_validate(event_raw)
            elif event_light.type == "WatchEvent":
                event_obj = github_models.WatchEvent.model_validate(event_raw)
            else:
                raise ValidationError(f"Unexpected event type: {event_light.type}")
            events_list.append(event_obj)
        except ValidationError as ex:
            print("Error, failed to deserialize the event which won't be processed")
            print(json.dumps(event_raw, indent=True))
            print(ex)
            continue

    return events_list


class Commit(NamedTuple):
    creator: str
    sha: str


class Branch(NamedTuple):
    ref: str
    repo: str
    commits: set[Commit]


class Action(NamedTuple):
    action: str
    date: datetime.datetime
    by: str


class Issue(NamedTuple):
    number: int
    title: str
    creator: str
    actions: list[Action]


class PullRequest(NamedTuple):
    number: int
    title: str
    creator: str
    linked_issues: set[Issue]
    linked_issues_ids: set[int]
    branch: Branch | None
    actions: list[Action]


class Repository(NamedTuple):
    name: str
    pull_requests: dict[str, PullRequest]
    issues: dict[str, Issue]
    branches: dict[str, Branch]


def main():
    if not GITHUB_TOKEN:
        raise Exception("GAR_GITHUB_TOKEN environment variable is mandatory.")

    if not INITIAL_EVENTS_PATH.exists():
        get_all_initial_events()

    messages: set[str] = set()
    events = load_events()

    # pull_requests: dict[str, PullRequest] = {}
    repositories: dict[str, Repository] = {}

    def event_is_pull_request(
        event: github_models.Event,
    ) -> TypeGuard[github_models.PullRequestEvent]:
        return isinstance(event, github_models.PullRequestEvent)

    for event in sorted(
        filter(event_is_pull_request, events), key=lambda event: event.created_at
    ):

        repo_name = event.repo.name
        if not repo_name in repositories:
            repo = Repository(name=repo_name, pull_requests={}, issues={}, branches={})
            repositories[repo_name] = repo
        else:
            repo = repositories[repo_name]

        issue_number = str(event.payload.pull_request.number)
        if issue_number in repo.pull_requests:
            pr = repo.pull_requests[issue_number]
        else:
            pr = PullRequest(
                number=event.payload.pull_request.number,
                title=event.payload.pull_request.title,
                creator=event.payload.pull_request.user.login,
                linked_issues=set(),
                linked_issues_ids=set(),
                branch=Branch(
                    ref=event.payload.pull_request.head.ref,
                    repo=event.payload.pull_request.head.repo.full_name,
                    commits=set(),
                ),
                actions=[],
            )
            repo.pull_requests[issue_number] = pr
        pr.actions.append(
            Action(
                action=f"PR {event.payload.action}",
                date=event.created_at,
                by=event.actor.login,
            )
        )
        if event.payload.pull_request.body:
            # update linked issues ids, in case it has been modified
            pr.linked_issues_ids.clear()
            pr.linked_issues_ids.update(
                int(match.group("id"))
                for match in ISSUE_PR_LINK_PATTERN.finditer(
                    event.payload.pull_request.body
                )
            )

    def event_is_issue_comment(
        event: github_models.Event,
    ) -> TypeGuard[github_models.IssueCommentEvent]:
        return isinstance(event, github_models.IssueCommentEvent)

    for event in sorted(
        filter(event_is_issue_comment, events), key=lambda event: event.created_at
    ):
        repo_name = event.repo.name
        if not repo_name in repositories:
            repo = Repository(name=repo_name, pull_requests={}, issues={}, branches={})
            repositories[repo_name] = repo
        else:
            repo = repositories[repo_name]

        if event.payload.issue.pull_request:
            issue_number = str(event.payload.issue.number)
            if issue_number in repo.pull_requests:
                pr = repo.pull_requests[issue_number]
            else:
                pr = PullRequest(
                    number=event.payload.issue.number,
                    title=event.payload.issue.title,
                    creator=event.payload.issue.user.login,
                    linked_issues=set(),
                    linked_issues_ids=set(),
                    branch=None,
                    actions=[],
                )
                repo.pull_requests[issue_number] = pr

            pr.actions.append(
                Action(
                    action=f"PR comment {event.payload.action}",
                    date=event.created_at,
                    by=event.actor.login,
                )
            )
        else:
            issue_number = str(event.payload.issue.number)
            if issue_number in repo.issues:
                issue = repo.issues[issue_number]
            else:
                issue = Issue(
                    number=event.payload.issue.number,
                    title=event.payload.issue.title,
                    creator=event.payload.issue.user.login,
                    actions=[],
                )
                repo.issues[issue_number] = issue

            issue.actions.append(
                Action(
                    action=f"Issue comment {event.payload.action}",
                    date=event.created_at,
                    by=event.actor.login,
                )
            )

    for repo in repositories.values():
        print(f"- {repo.name}")
        for pr in repo.pull_requests.values():
            message = f"  - PR #{pr.number} (by {pr.creator}) {pr.title}"
            if len(pr.linked_issues_ids) > 0:
                message += f", fixing issues {pr.linked_issues_ids}"
            print(message)
            for action in pr.actions:
                print(f"    - {action.action} by {action.by} at {action.date}")
        for issue in repo.issues.values():
            message = f"  - Issue #{issue.number} (by {issue.creator}) {issue.title}"
            print(message)
            for action in issue.actions:
                print(f"    - {action.action} by {action.by} at {action.date}")

    # for event in events:
    #     if isinstance(event, github_models.IssueCommentEvent):
    #         if event.payload.issue.pull_request:
    #             kind = "PR"
    #         else:
    #             kind = "Issue"
    #         message = f"{event.repo.name}: {kind} #{event.payload.issue.number} (by {event.payload.issue.user.login}): {event.payload.issue.title}"
    #         messages.add(message)

    # for message in sorted(messages):
    #     print(message)


if __name__ == "__main__":
    main()
