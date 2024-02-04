import requests
import os
import datetime
import re
import json
from pathlib import Path

from github_activity_report import github_models

from pydantic import ValidationError

USERNAME = os.getenv("GAR_USERNAME", "benoit74")
GITHUB_TOKEN = os.getenv("GAR_GITHUB_TOKEN", None)
START_DATETIME = datetime.datetime.fromisoformat("2024-01-29T17:00:00Z")


def get_resp_header(result: requests.Response, header: str) -> str:
    value = result.headers.get(header)
    assert value
    return value


LINK_PATTERN = re.compile(r'<(?P<url>.+?)>; rel="(?P<rel>.+?)"')
INITIAL_EVENTS_PATH = Path("output/initial_events.json")


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
            tz=datetime.timezone.utc,
        )
        events = response.json()
        all_events.extend(events)
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

    print(f"Total: {len(all_events)} events found")
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


def main():
    if not GITHUB_TOKEN:
        raise Exception("GAR_GITHUB_TOKEN environment variable is mandatory.")

    if not INITIAL_EVENTS_PATH.exists():
        get_all_initial_events()

    messages: set[str] = set()
    events = load_events()
    for event in events:
        if isinstance(event, github_models.IssueCommentEvent):
            if event.payload.issue.pull_request:
                kind = "PR"
            else:
                kind = "Issue"
            message = f"{event.repo.name}: {kind} #{event.payload.issue.number} (by {event.payload.issue.user.login}): {event.payload.issue.title}"
            messages.add(message)

    for message in sorted(messages):
        print(message)


if __name__ == "__main__":
    main()
