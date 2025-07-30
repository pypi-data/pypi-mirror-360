# Hackbot

CLI tool for source code analysis using the [GatlingX Hackbot](https://hackbot.co/) service.

## Installation

```bash
pip install hackbot
```

## Performing a scan
Execute the following command to perform a scan.
Visit your dashboard at [hackbot.co](https://hackbot.co/dashboard/api-keys/) to retrieve your API key.
Either set the API key as an environment variable `HACKBOT_API_KEY` or pass it as an argument to the command line tool.

```bash
cd your-project-directory
python -m hackbot run --api-key <api-key>
```

You will then see various messages and results in the terminal. If `--output` is provided, the complete output will also be written to a JSON file.
At the end of the scan, you will get a link to the dashboard where you can view the results.

## Learning from Security Resources
Hackbot also supports a learn command that allows it to update its checklist based on external resources.
For example, to learn from a blog post, run:

```bash
python -m hackbot learn --url https://blog.openzeppelin.com/web3-security-auditors-2024-rewind
```

This command will fetch additional checklist data to enhance Hackbot's analysis.

## CLI options
See `python -m hackbot --help` for more information
