## Create personal access token with repo:status and repo_deployment access
TODO: verify and understand scope of this request

## The PAT can be used as a password
- `curl -u "user:PAT"`
- `curl -H "Authorization: token PAT" --data @test.json https://api.github.com/repos/terrywbrady/repo-tagger/releases`

## Payload test.json
```
{
  "tag_name": "tag11",
  "target_commitish": "master",
  "name": "Merritt Release",
  "body": "## Header\n
  This is a message\n
  ### Hello\n
  This is another message",
  "draft": false,
  "prerelease": false
}
```
