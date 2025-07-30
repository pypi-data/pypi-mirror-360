**thoughtful** is a collection of open-source libraries and tools for Robot Process
Automation (RPA) development. The goal of this project is to provide a set of
for supervising bot execution, and enabling these bots to do more.

[![PyPi version](https://badgen.net/pypi/v/thoughtful/)](https://pypi.org/project/thoughtful/)
[![Supported Versions](https://img.shields.io/pypi/pyversions/thoughtful.svg)](https://pypi.org/project/thoughtful)
[![Downloads](https://pepy.tech/badge/thoughtful/month)](https://pepy.tech/project/thoughtful)

[//]: # "[![GitHub release](https://img.shields.io/github/release/Thoughtful-Automation/supervisor.svg)](https://GitHub.com/Naereen/StrapDown.js/releases/)"

This project is:

- Open-source: [GitHub][url:gh]
- Owned by [thoughtful][url:ta]
- Licensed under the [Apache License 2.0][url:al]

Links:

- [Homepage][url:gh]
- [Documentation][url:docs]
- [PyPI][url:pypi]

**thoughtful** is available on [PyPI][url:pypi] and can be installed using pip:

```sh
pip install thoughtful
```

---

**thoughtful** officially supports Python 3.10+.

---

# Libraries

## Supervisor

Supervisor is a Workflow Engine for Digital Workers that constructs
and broadcasts a detailed and structured telemetric log, called the Run Report.

### Detailed documentation

Detailed documentation on how to utilize Supervisor can be found [here][url:supervisor_docs].

### Usage

```python
from thoughtful.supervisor import step, step_scope, supervise, set_step_status


# using the step decorator
@step("2")
def step_2(name: str) -> bool:
    print(f'Hello {name}')
    return True  # some condition

def main() -> None:
    # using the step_scope context manager
    with step_scope('1') as step_context:
        try:
            print("Getting credentials")
            # ...
        except Exception as e:
            # set step status using method
            step_context.set_status("warning")

    if not step_2():
        # set step status using function
        set_step_status("2", "fail")

if __name__ == '__main__':
    with supervise():
        main()
```

### OpenTelemetry tracing (optional)

Supervisor can emit OpenTelemetry traces so you can visualize your bot runs in any OTLP-compatible backend.

Enable tracing by passing OTLP configuration to `supervise()`:

```python
from thoughtful.supervisor import supervise
from t_vault import bw_login_from_env

# Login to Bitwarden first (credentials are automatically pulled if not explicitly provided)
bw_login_from_env()

# Run the workflow with tracing enabled
with supervise(
    manifest="manifest.yaml",
    otlp_config={
        "endpoint": "https://otel.thoughthub.thoughtful-dev.ai/v1/traces",
        # Headers are optional - if not provided, credentials will be automatically pulled from t_vault
    }
):
    main()
```

**Note:** When using Thoughtful's public endpoint, if you don't explicitly provide authorization headers in the `otlp_config`, the supervisor will automatically attempt to pull credentials from `t_vault` using the `bw_get_item('otl-dev-password')` method.

Under the hood the supervisor initializes OpenTelemetry **automatically** when an OTLP configuration is provided.
It opens a single root span for the entire run and every `step_scope` / `@step` becomes a child span, so your backend will show a neat, hierarchical trace of the whole workflow.

## Screen Recorder

The ScreenRecorder library facilitates the recording of screen activity from a
programmatic browser session and generates a video file of the recorded session.

### Detailed documentation

Detailed documentation on how to utilize Screen Recorder can be found [here][url:screen_recorder_docs].

### Prerequisites

Ensure you have already downloaded `FFmpeg` as it is utilized to create the video recording.

https://www.ffmpeg.org/download.html

### Installation

Install the optional `screen-recorder` extras

#### Poetry

```shell
poetry install -E screen-recorder
```

#### Pip

```shell
pip install thoughtful[screen-recorder]
```

### Usage

**WARNING: It is essential that you call `end_recording` at the end of a recording.**

**If you do not call `end_recording`, the recording threads will continue to run until your program ends and a
video will not be created.**

```python
from thoughtful.screen_recorder import ScreenRecorder, BrowserManager
from RPA.Browser.Selenium import Selenium # This dependency must be installed separately

class YoutubeScraper(ScreenRecorder):
    def __init__(self) -> None:
        self._selenium_instance = Selenium()
        super().__init__(browser_manager=BrowserManager(instance=self._selenium_instance))

youtube_scraper = YoutubeScraper()
try:
    # ... Perform actions here ...
finally:
    if youtube_scraper:
        # We recommend calling `end_recording` in a `finally` block to ensure that
        # video processing occurs and all recording threads are terminated even if the Process fails
        youtube_scraper.end_recording()
```

## Contributing

Contributions to **thoughtful** are welcome!

To get started, see the [contributing guide](CONTRIBUTING.md).

---

Made with ❤️ by

[![Thoughtful](https://user-images.githubusercontent.com/1096881/141985289-317c2e72-3c2d-4e6b-800a-0def1a05f599.png)][url:ta]

---

This project is open-source and licensed under the terms of the [Apache License 2.0][url:al].

<!--  Link References -->

[url:ta]: https://www.thoughtful.ai/
[url:gh]: https://github.com/Thoughtful-Automation/supervisor
[url:pypi]: https://pypi.org/project/thoughtful/
[git:issues]: https://github.com/Thoughtful-Automation/supervisor/issues
[url:docs]: https://www.notion.so/thoughtfulautomation/Thoughtful-Library-c0333f67989d4044aa0a595eaf8fd07b
[url:al]: http://www.apache.org/licenses/LICENSE-2.0
[url:supervisor_docs]: https://www.notion.so/thoughtfulautomation/How-to-develop-with-Supervisor-4247b8d2a5a747b6bff1d232ad395e9c
[url:screen_recorder_docs]: https://www.notion.so/thoughtfulautomation/ScreenRecorder-67380d38b18345f9bac039ff0ef38b0a
