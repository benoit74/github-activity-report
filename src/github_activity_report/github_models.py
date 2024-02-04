import datetime
from pydantic import BaseModel, Field, RootModel
from typing import Literal, Union
from typing_extensions import Annotated


class EventActor(BaseModel):
    id: int
    login: str
    display_login: str | None = Field(default=None)
    gravatar_id: str | None
    url: str
    avatar_url: str


class EventRepository(BaseModel):
    id: int
    name: str
    url: str


class EventOrg(BaseModel):
    id: int
    gravatar_id: str
    url: str
    avatar_url: str


class EventBase(BaseModel):
    id: str
    actor: EventActor
    repo: EventRepository
    created_at: datetime.datetime
    org: EventOrg | None = Field(default=None)


class EventLight(EventBase):
    type: str


class User(BaseModel):
    login: str
    id: int
    node_id: str
    avatar_url: str
    gravatar_id: str
    url: str
    html_url: str
    followers_url: str
    following_url: str
    gists_url: str
    starred_url: str
    subscriptions_url: str
    organizations_url: str
    repos_url: str
    events_url: str
    received_events_url: str
    type: str
    site_admin: bool


class Label(BaseModel):
    id: int
    node_id: str
    url: str
    name: str
    color: str
    default: bool
    description: str | None


class Reactions(BaseModel):
    url: str
    total_count: int
    plus_1: int = Field(alias="+1")
    minus_1: int = Field(alias="-1")
    laugh: int
    hooray: int
    confused: int
    heart: int
    rocket: int
    eyes: int


class Milestone(BaseModel):
    url: str
    html_url: str
    labels_url: str
    id: int
    node_id: str
    number: int
    title: str
    description: str
    creator: User
    open_issues: int
    closed_issues: int
    state: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    due_on: datetime.datetime | None
    closed_at: datetime.datetime | None


class IssuePullRequest(BaseModel):
    url: str
    html_url: str
    diff_url: str
    patch_url: str
    merged_at: datetime.datetime | None


class Issue(BaseModel):
    url: str
    repository_url: str
    labels_url: str
    comments_url: str
    events_url: str
    html_url: str
    id: int
    node_id: str
    number: int
    title: str
    user: User
    labels: list[Label]
    state: str
    locked: bool
    assignee: User | None
    assignees: list[User]
    milestone: Milestone | None
    comments: int
    created_at: datetime.datetime | None
    updated_at: datetime.datetime | None
    closed_at: datetime.datetime | None
    author_association: str
    body: str | None
    reactions: Reactions
    timeline_url: str
    active_lock_reason: None  # this is probably wrong but we lack an example
    performed_via_github_app: None  # this is probably wrong but we lack an example
    state_reason: str | None  # this is probably wrong but we lack an example
    pull_request: IssuePullRequest | None = Field(default=None)


class CommentLight(BaseModel):
    url: str
    html_url: str
    id: int
    node_id: str
    user: User
    created_at: str
    updated_at: str
    author_association: str
    body: str
    reactions: Reactions


class Comment(CommentLight):
    issue_url: str
    performed_via_github_app: bool | None


class CommitCommentEventPayload(BaseModel):
    action: str
    toto: str  # fake, just to raise an error and fix next time


class CommitCommentEvent(EventBase):
    type: Literal["CommitCommentEvent"]
    payload: CommitCommentEventPayload


class CreateEventPayload(BaseModel):
    ref: str | None
    ref_type: str
    master_branch: str
    description: str
    pusher_type: str


class CreateEvent(EventBase):
    type: Literal["CreateEvent"]
    payload: CreateEventPayload


class DeleteEventPayload(BaseModel):
    ref: str
    ref_type: str


class DeleteEvent(EventBase):
    type: Literal["DeleteEvent"]
    payload: DeleteEventPayload


class IssueCommentEventPayload(BaseModel):
    action: str
    issue: Issue
    comment: Comment


class IssueCommentEvent(EventBase):
    type: Literal["IssueCommentEvent"]
    payload: IssueCommentEventPayload


class IssuesEventPayload(BaseModel):
    action: str
    issue: Issue
    assignee: User | None = Field(default=None)
    label: Label | None = Field(default=None)


class IssuesEvent(EventBase):
    type: Literal["IssuesEvent"]
    payload: IssuesEventPayload


class MemberEventPayload(BaseModel):
    action: str
    member: User


class MemberEvent(EventBase):
    type: Literal["MemberEvent"]
    payload: MemberEventPayload


class PublicEvent(EventBase):
    type: Literal["PublicEvent"]
    payload: None = Field(default=None)


class License(BaseModel):
    key: str
    name: str
    spdx_id: str
    url: str
    node_id: str


class Repo(BaseModel):
    allow_forking: bool
    archive_url: str
    archived: bool
    assignees_url: str
    blobs_url: str
    branches_url: str
    clone_url: str
    collaborators_url: str
    comments_url: str
    commits_url: str
    compare_url: str
    contents_url: str
    contributors_url: str
    created_at: str
    default_branch: str
    deployments_url: str
    description: str
    disabled: bool
    downloads_url: str
    events_url: str
    fork: bool
    forks_count: int
    forks_url: str
    forks: int
    full_name: str
    git_commits_url: str
    git_refs_url: str
    git_tags_url: str
    git_url: str
    has_discussions: bool
    has_downloads: bool
    has_issues: bool
    has_pages: bool
    has_projects: bool
    has_wiki: bool
    homepage: str | None
    hooks_url: str
    html_url: str
    id: int
    is_template: bool
    issue_comment_url: str
    issue_events_url: str
    issues_url: str
    keys_url: str
    labels_url: str
    language: str | None
    languages_url: str
    license: License
    merges_url: str
    milestones_url: str
    mirror_url: None
    name: str
    node_id: str
    notifications_url: str
    open_issues_count: int
    open_issues: int
    owner: User
    private: bool
    pulls_url: str
    pushed_at: str
    releases_url: str
    size: int
    ssh_url: str
    stargazers_count: int
    stargazers_url: str
    statuses_url: str
    subscribers_url: str
    subscription_url: str
    svn_url: str
    tags_url: str
    teams_url: str
    topics: list[str]
    trees_url: str
    updated_at: str
    url: str
    visibility: str
    watchers_count: int
    watchers: int
    web_commit_signoff_required: bool


class Branch(BaseModel):
    label: str
    ref: str
    sha: str
    user: User
    repo: Repo


class Link(BaseModel):
    href: str


class PullRequestLinks(BaseModel):
    self: Link
    html: Link
    issue: Link
    comments: Link
    review_comments: Link
    review_comment: Link
    commits: Link
    statuses: Link


class PullRequest(BaseModel):
    active_lock_reason: None
    additions: int
    assignee: User | None
    assignees: list[User]
    author_association: str
    auto_merge: None
    base: Branch
    body: str | None
    changed_files: int
    closed_at: datetime.datetime | None
    comments_url: str
    comments: int
    commits_url: str
    commits: int
    created_at: datetime.datetime
    deletions: int
    diff_url: str
    draft: bool
    head: Branch
    html_url: str
    id: int
    issue_url: str
    labels: list[Label]
    links: PullRequestLinks = Field(alias="_links")
    locked: bool
    maintainer_can_modify: bool
    merge_commit_sha: str | None
    mergeable_state: str
    mergeable: bool | None
    merged_at: datetime.datetime | None
    merged_by: User | None
    merged: bool
    milestone: Milestone | None
    node_id: str
    number: int
    patch_url: str
    rebaseable: bool | None
    requested_reviewers: list[User]
    requested_teams: list[str]  # probably wrong list type
    review_comment_url: str
    review_comments_url: str
    review_comments: int
    state: str
    statuses_url: str
    title: str
    updated_at: datetime.datetime
    url: str
    user: User


class PullRequestEventPayload(BaseModel):
    action: str
    number: int
    pull_request: PullRequest


class PullRequestEvent(EventBase):
    type: Literal["PullRequestEvent"]
    payload: PullRequestEventPayload


class ForkEventPayload(BaseModel):
    forkee: Repo


class ForkEvent(EventBase):
    type: Literal["ForkEvent"]
    payload: ForkEventPayload


class GollumEventPage(BaseModel):
    page_name: str
    title: str
    summary: str | None
    action: str
    sha: str
    html_url: str


class GollumEventPayload(BaseModel):
    pages: list[GollumEventPage]


class GollumEvent(EventBase):
    type: Literal["GollumEvent"]
    payload: GollumEventPayload


class ReviewLinks(BaseModel):
    html: Link
    pull_request: Link


class Review(BaseModel):
    id: int
    node_id: str
    user: User
    body: str | None
    commit_id: str
    submitted_at: str
    state: str
    html_url: str
    pull_request_url: str
    author_association: str
    links: ReviewLinks = Field(alias="_links")


class PullRequestLight(BaseModel):
    active_lock_reason: None
    assignee: User | None
    assignees: list[User]
    author_association: str
    auto_merge: None
    base: Branch
    body: str
    closed_at: datetime.datetime | None
    comments_url: str
    commits_url: str
    created_at: datetime.datetime
    diff_url: str
    draft: bool
    head: Branch
    html_url: str
    id: int
    issue_url: str
    labels: list[Label]
    links: PullRequestLinks = Field(alias="_links")
    locked: bool
    merge_commit_sha: str | None
    merged_at: datetime.datetime | None
    milestone: Milestone | None
    node_id: str
    number: int
    patch_url: str
    requested_reviewers: list[User]
    requested_teams: list[str]  # probably wrong list type
    review_comment_url: str
    review_comments_url: str
    state: str
    statuses_url: str
    title: str
    updated_at: datetime.datetime
    url: str
    user: User


class PullRequestReviewEventPayload(BaseModel):
    action: str
    pull_request: PullRequestLight
    review: Review


class PullRequestReviewEvent(EventBase):
    type: Literal["PullRequestReviewEvent"]
    payload: PullRequestReviewEventPayload


class PullRequestReviewCommentEventPayload(BaseModel):
    action: str
    pull_request: PullRequestLight
    comment: CommentLight


class PullRequestReviewCommentEvent(EventBase):
    type: Literal["PullRequestReviewCommentEvent"]
    payload: PullRequestReviewCommentEventPayload


class Thread(BaseModel):
    toto: int  # fake schema, just to raise an error when we encounter this type


class PullRequestReviewThreadEventPayload(BaseModel):
    action: str
    pull_request: PullRequestLight
    thread: Thread


class PullRequestReviewThreadEvent(EventBase):
    type: Literal["PullRequestReviewThreadEvent"]
    payload: PullRequestReviewThreadEventPayload


class CommitAuthor(BaseModel):
    email: str
    name: str


class Commit(BaseModel):
    sha: str
    author: CommitAuthor
    message: str
    distinct: bool
    url: str


class PushEventPayload(BaseModel):
    repository_id: int
    push_id: int
    size: int
    distinct_size: int
    ref: str
    head: str
    before: str
    commits: list[Commit]


class PushEvent(EventBase):
    type: Literal["PushEvent"]
    payload: PushEventPayload


class Release(BaseModel):
    url: str
    assets_url: str
    upload_url: str
    html_url: str
    id: int
    author: User
    node_id: str
    tag_name: str
    target_commitish: str
    name: str
    draft: bool
    prerelease: bool
    created_at: str
    published_at: str
    assets: list[str]  # probably wrong
    tarball_url: str
    zipball_url: str
    body: str | None
    short_description_html: str
    is_short_description_html_truncated: bool


class ReleaseEventPayload(BaseModel):
    action: str
    release: Release


class ReleaseEvent(EventBase):
    type: Literal["ReleaseEvent"]
    payload: ReleaseEventPayload


class SponsorshipEventPayload(BaseModel):
    action: str
    effective_date: datetime.datetime | None


class SponsorshipEvent(EventBase):
    type: Literal["SponsorshipEvent"]
    payload: SponsorshipEventPayload


class WatchEventPayload(BaseModel):
    action: str


class WatchEvent(EventBase):
    type: Literal["WatchEvent"]
    payload: WatchEventPayload


Event = Annotated[
    Union[
        CommitCommentEvent,
        CreateEvent,
        DeleteEvent,
        ForkEvent,
        GollumEvent,
        IssueCommentEvent,
        IssuesEvent,
        MemberEvent,
        PublicEvent,
        PullRequestEvent,
        PullRequestReviewEvent,
        PullRequestReviewCommentEvent,
        PullRequestReviewThreadEvent,
        PushEvent,
        ReleaseEvent,
        SponsorshipEvent,
        WatchEvent,
        WatchEvent,
    ],
    Field(discriminator="type"),
]

Events = RootModel[list[Event]]
