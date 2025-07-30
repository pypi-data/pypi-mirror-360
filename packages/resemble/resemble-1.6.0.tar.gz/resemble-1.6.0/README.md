# resemble.ai API

[resemble.ai](https://resemble.ai) is a state-of-the-art natural voice cloning and synthesis provider. Best of all, the platform is accessible by using our public API! Sign up [here](https://app.resemble.ai) to get an API token!

This repository hosts a Python library for convenient usage of the [Resemble API](https://docs.resemble.ai).


# Quick start

```python
from resemble import Resemble

Resemble.api_key('your_api_key')

project = Resemble.v2.projects.get('project_uuid')
voice = Resemble.v2.voices.get('voice_uuid')

clip = Resemble.v2.clips.create_sync('project_uuid', 'voice_uuid', 'This is a test')
```

## Streaming
The Streaming API is currently in beta and is not available to all users. Please reach out to team@resemble.ai to inquire more.

Streaming example:
```python
from resemble import Resemble

Resemble.api_key('your_api_key')
Resemble.syn_server_url('your_resemble_synthesis_server_url') # Extra configuration required for streaming

for chunk in Resemble.v2.clips.stream('project_uuid', 'vouce_uuid', 'This is a test'):
    # do something with the `chunk` of audio data, such as feeding it into a streaming audio player
    pass
```

# Development

The library files are located in `resemble/`

# Testing

Note that currently the test suite performs real actions against the Resemble AI platform (e.g., creating projects, retrieving clips, updating voices, _et cetera_).

```bash
# For tests that do NOT require a voice
$ TEST_API_KEY=<...> TEST_BASE_URL=<...> python3 -m unittest

# For tests that do require a voice
$ TEST_API_KEY=<...> TEST_BASE_URL=<...> TEST_VOICE_UUID=<...> python3 -m unittest
```

# Publishing new versions

You need the `build` and `twine` pip packages. (`pip3 install build twine`)

1. `git status`: Make sure your working directory has no pending changes.
2. Update the version attribute in `setup.py`.
3. `git commit`: Commit this version change.
4. Build the package: `make pkg.build`
5. (optional) Publish to the test index:
  ```sh
  make pkg.publish.test
  ```
6. Publish to the index
  ```sh
  make pkg.publish
  ```
