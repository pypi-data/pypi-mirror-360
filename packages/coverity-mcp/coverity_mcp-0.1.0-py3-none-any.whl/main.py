import json
import argparse
from typing import Annotated, Literal, Optional
import datetime

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
from pydantic import BaseModel, Field
import requests
from requests.auth import HTTPBasicAuth

def trim_left(s: str, prefix: str) -> str:
    if s.startswith(prefix):
        return s[len(prefix):]
    return s

Classification = Literal['Unclassified', 'Pending', 'False Positive', 'Intentional', 'Bug']

class DiagnosticsEvent(BaseModel):
    description: Annotated[str, Field(description="Description of event")]
    file: Annotated[str, Field(description="File path where event happened")]
    line: Annotated[int, Field(description="Line number where event happened")]
    event_kind: Annotated[str, Field(description="Kind of event")]

class IssueDiagnostics(BaseModel):
    id: Annotated[int, Field(description="Issue ID")]
    description: Annotated[str, Field(description="Brief issue description")]
    events: Annotated[list[DiagnosticsEvent], Field(description="Sequence of events leading to problem")]

class IssueInfo(BaseModel):
    cid: Annotated[int, Field(description="Issue ID")]
    issue_kind: Annotated[str, Field(description="Brief issue description")]
    owner: Annotated[str, Field(description="User who is responsible for fixing issue")]
    startrek_issue: Annotated[Optional[str], Field(description="Startrek issue key")]
    status: Annotated[Literal['New', 'Triaged'], Field(description="Triage status")]
    classification: Annotated[Classification, Field(description="Classification: whether found issue is real bug or not")]
    severity: Annotated[Literal['Minor', 'Moderate', 'Major', 'Unspecified'], Field(description="Severity")]
    last_detected: Annotated[datetime.date, Field(description="Last detection date")]
    last_detected_version: Annotated[str, Field(description="Last detection build version")]
    last_detected_target: Annotated[str, Field(description="Last detection build platform, for example: linux64")]
    last_detected_stream: Annotated[str, Field(description="Last detection Coverity stream (build configuration)")]

class StreamInfo(BaseModel):
    name: Annotated[str, Field(description="Name of the stream")]
    description: Annotated[str, Field(description="Description of the stream")]
    primaryProjectName: Annotated[str, Field(description="Primary project name")]
    triageStoreName: Annotated[str, Field(description="Triage store name for the stream")]

class CoverityClient:
    def __init__(self, opts):
        self.base_url = opts.base_url
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(opts.username, opts.key)
        self.session.verify = opts.certificate_path or True
        self.trim_path_prefix = opts.trim_path_prefix

    def get_stream_info(self, stream_name: str) -> Optional[StreamInfo]:
        response = self.session.get(f"{self.base_url}/streams/{stream_name}")
        response.raise_for_status()
        data = response.json()
        return StreamInfo.model_validate(data['streams'][0])

    def get_issue_info(self, project_name: str, id: int) -> Optional[IssueInfo]:
        response = self.session.post(
            f"{self.base_url}/issues/search",
            json=dict(
                filters=[
                    dict(
                        columnKey="cid",
                        matchMode="oneOrMoreMatch",
                        matchers=[
                            dict(type="idMatcher", id=id),
                        ]
                    ),
                    dict(
                        columnKey="project",
                        matchMode="oneOrMoreMatch",
                        matchers=[
                            {"type": "nameMatcher", "name": project_name, "class": "Project"},
                        ]
                    ),
                ],
                columns=[
                    # Basic fields
                    "cid", "displayType", "owner", "column_custom_Startrek ticket",
                    "status", "project", "classification", "severity",
                    # Last detection
                    "lastDetected", "lastDetectedVersion", "lastDetectedTarget", "lastDetectedStream",
                ],
            ),
        )
        response.raise_for_status()
        data = response.json()

        if len(data['rows']) == 0:
            return None

        if len(data['rows']) > 1:
            raise Exception("Unexpected number of rows")

        row = data['rows'][0]
        info = {c['key']: c['value'] for c in row}

        return IssueInfo(
            cid = int(info['cid']),
            issue_kind = info['displayType'],
            owner = info['owner'],
            startrek_issue = info['column_custom_Startrek ticket'],
            status = info['status'],
            classification = info['classification'],
            severity = info['severity'],
            last_detected = datetime.datetime.strptime(info['lastDetected'], "%m/%d/%y").date(),
            last_detected_version = info['lastDetectedVersion'],
            last_detected_target = info['lastDetectedTarget'],
            last_detected_stream = info['lastDetectedStream'],
        )

    def get_issue_diagnostics(self, stream: str, id: int) -> Optional[IssueDiagnostics]:
        response = self.session.get(
            f"{self.base_url}/issues/sourceCodeInfo",
            params=dict(streamName=stream, cid=id),
        )
        response.raise_for_status()
        data = response.json()

        # Choose occurence with largest ID
        occurences = data['issueOccurrences']
        max_occurence_id = max(o['id'] for o in occurences)
        occurence = [o for o in occurences if o['id'] == max_occurence_id][0]

        return IssueDiagnostics(
            id = int(occurence['id']),
            description = occurence['longDescription'],
            events = [DiagnosticsEvent(
                description = e['eventDescription'],
                file = trim_left(e['file']['filePathname'], self.trim_path_prefix),
                line = int(e['lineNumber']),
                event_kind = e['eventTag'],
            ) for e in occurence['events']],
        )

    def triage_issue(
        self,
        store_name: str,
        id: int,
        classification: Optional[Classification],
        action: str,
        comment: str,
    ) -> None:
        attrs = [
            dict(attributeName="Action", attributeValue=action),
            dict(attributeName="Comment", attributeValue=comment),
        ]
        if classification:
            attrs.append(dict(attributeName="Action", attributeValue=action))

        response = self.session.put(
            f"{self.base_url}/issues/triage",
            json=dict(
                cids=[id],
                attributeValuesList=attrs,
            ),
            params=dict(triageStoreName=store_name),
        )
        response.raise_for_status()

def run(opts):
    mcp = FastMCP("Coverity")

    @mcp.tool()
    def get_issue_info(
        project_name: Annotated[str, Field(description="Name of Coverity project")],
        id: Annotated[int, Field(description="Issue ID")]
    ) -> Optional[IssueInfo]:
        """Get details of Coverity issue.

        Returns issue details:
        * Issue description
        """
        client = CoverityClient(opts)
        return client.get_issue_info(project_name, id)

    @mcp.tool()
    def get_issue_diagnostics(
        project_name: Annotated[str, Field(description="Name of Coverity project")],
        id: Annotated[int, Field(description="Issue ID")]
    ) -> Optional[IssueDiagnostics]:
        """Get diagnostics of Coverity issue.

        Returns issue details:
        * Issue description
        * Chain of found conditions under which issue appears, with references
          to exact file and lines.
        """
        client = CoverityClient(opts)
        info = client.get_issue_info(project_name, id)
        if not info:
            return None
        return client.get_issue_diagnostics(info.last_detected_stream, id)

    @mcp.tool()
    def triage_issue(
        project_name: Annotated[str, Field(description="Name of Coverity project")],
        id: Annotated[int, Field(description="Issue ID")],
        classification: Annotated[Classification, Field(description="Issue classification")],
        action: Annotated[str, Field(description="Action to set, like 'Fix required' or 'Fix Submitted'")],
        comment: Annotated[str, Field(description="Triage comment")]
    ) -> None:
        """Triage Coverity issue.
        """
        client = CoverityClient(opts)
        info = client.get_issue_info(project_name, id)
        assert info
        stream_info = client.get_stream_info(info.last_detected_stream)
        assert stream_info
        return client.triage_issue(stream_info.triageStoreName, id, classification, action, comment)

    # Add a dynamic greeting resource
    @mcp.prompt(title="Fix Coverity issue")
    def fix_issue(stream: str, id: int) -> list[base.Message]:
        return [
            base.UserMessage(f"Get information about Coverity issue and fix it. Issue details: {json.dumps(dict(stream=stream, id=id))}"),
        ]

    mcp.run()

def test_info(opts):
    client = CoverityClient(opts)
    info = client.get_issue_info(opts.project, opts.id)
    if info:
        print(info.model_dump_json())
    else:
        print('null')

def test_stream_info(opts):
    client = CoverityClient(opts)
    info = client.get_stream_info(opts.stream)
    if info:
        print(info.model_dump_json())
    else:
        print('null')

def test_diagnostics(opts):
    client = CoverityClient(opts)
    diagnostics = client.get_issue_diagnostics(opts.stream, opts.id)
    if diagnostics:
        print(diagnostics.model_dump_json())
    else:
        print('null')

def test_triage(opts):
    client = CoverityClient(opts)
    client.triage_issue(opts.store, opts.id, opts.classification, opts.action, opts.comment)
    print('ok')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', type=str, required=True)
    parser.add_argument('--username', type=str, required=True)
    parser.add_argument('--key', type=str, required=True)
    parser.add_argument('--trim-path-prefix', type=str, default='')
    parser.add_argument('--certificate-path', type=str, default=None)

    subparsers = parser.add_subparsers(required=True)

    test_get_cmd = subparsers.add_parser('test-info')
    test_get_cmd.set_defaults(func=test_info)
    test_get_cmd.add_argument('project', type=str)
    test_get_cmd.add_argument('id', type=int)

    test_get_cmd = subparsers.add_parser('test-diagnostics')
    test_get_cmd.set_defaults(func=test_diagnostics)
    test_get_cmd.add_argument('stream', type=str)
    test_get_cmd.add_argument('id', type=int)

    test_triage_cmd = subparsers.add_parser('test-triage')
    test_triage_cmd.set_defaults(func=test_triage)
    test_triage_cmd.add_argument('store', type=str)
    test_triage_cmd.add_argument('id', type=int)
    test_triage_cmd.add_argument('--classification', type=str)
    test_triage_cmd.add_argument('--action', type=str, required=True)
    test_triage_cmd.add_argument('--comment', type=str, required=True)

    test_stream_cmd = subparsers.add_parser('test-stream-info')
    test_stream_cmd.set_defaults(func=test_stream_info)
    test_stream_cmd.add_argument('stream', type=str)

    run_cmd = subparsers.add_parser('run')
    run_cmd.set_defaults(func=run)

    opts = parser.parse_args()
    opts.func(opts)
