# LinkIQ

> **Important:** Before using LinkIQ, it is critical to read the [LinkedIn User Agreement](https://www.linkedin.com/legal/user-agreement#dos). You are solely responsible for using this software in a manner compliant with LinkedIn's terms and conditions.

> Please also read the LinkIQ LICENSE terms and conditions before proceeding.

LinkIQ is your **personal** LinkedIn Copilot. This software is designed to help you automate repetitive tasks such as qualifying profiles as leads and sending outreach messages.

## Features

LinkIQ can:
- Gather profiles of users who have viewed your profile or reacted to your posts
- Collect profiles as you conduct searches
- Qualify these profiles using criteria that you set up
- Automatically reach out with connection requests and first messages

## Installation

This product has been tested on macOS Sequoia 15.5 with Python version 3.13.3. Create a virtual environment to prevent LinkIQ dependencies from conflicting with your system installation, then install LinkIQ using pip.

```bash
python3 -m venv venv
source venv/bin/activate
pip install linkiq
playwright install
linkiq --help
```

## Usage

```bash
linkiq --help          
Usage: linkiq [OPTIONS] COMMAND [ARGS]...

  LinkIQ CLI - Your LinkedIn Growth Assistant

Options:
  --help  Show this message and exit.

Commands:
  camp       Manage campaigns.
  gather     Gather LinkedIn data like profile views and post reactions.
  leadgen    Search and gather LinkedIn profiles.
  outreach   Send messages to qualified leads
  run        Run both background scheduler and UI.
  scheduler  Run only the scheduler.
  search     Search and gather LinkedIn profiles.
  view       Launch just the FastAPI UI server.
```

## Commands

### Gather Profiles: `gather`

This command gathers profiles of users who viewed your profile and those who reacted to your posts. Profile viewers are collected for the last 14 days, and reactions are collected for posts from the last 7 days. You can choose to gather only profile viewers (`-v` flag) or only post reactions (`-p` flag). By default, the command gathers from both profile views and post reactions.

```bash
linkiq gather --help
Usage: linkiq gather [OPTIONS]

  Gather LinkedIn data like profile views and post reactions.

Options:
  -v, --profile-views  Gather profile views only.
  -p, --post-reaction  Gather post reactions only.
  --help               Show this message and exit.
```

### Search Profiles: `search`

You can gather profiles by conducting specific searches.

```bash
linkiq search --help 
Usage: linkiq search [OPTIONS]

  Search and gather LinkedIn profiles.

Options:
  -m, --max-profiles INTEGER  Maximum number of profiles to gather per search
                              round.  [default: 100]
  --help                      Show this message and exit.
```

### Campaign Management: `camp`

Campaigns allow you to define which profiles are of interest. You create a campaign with a name and specify the criteria to qualify profiles. The qualification criteria can be based on:

- `include_keywords`: Include profiles if any keyword is found in the name, title, or company of the profile
- `exclude_keywords`: Exclude profiles if any of the keywords are found in the name, title, or company of the profile

If you leave these fields empty, any profile will be qualified.

For each campaign, you can specify the messages to send to qualified leads:

- `connect_message`: The message to send along with the connection request
- `first_message`: The message to send if the qualified lead is already connected

Your campaign consists of: name, include/exclude keywords, and connect/first message.

#### Create Campaign: `camp create`

To create a campaign:

```bash
linkiq camp create
```

#### List Campaigns: `camp list`

To list campaigns:

```bash
linkiq camp list
```

#### Get Campaign Details: `camp get`

To get campaign details:

```bash
linkiq camp get
```

### Lead Generation: `leadgen`

A lead is a profile that is qualified for a specific campaign. **You must have at least one campaign to qualify a profile.** LinkIQ will automatically load the profile and, based on the provided keywords, qualify the lead.

```bash
linkiq leadgen --help
Usage: linkiq leadgen [OPTIONS]

  Search and gather LinkedIn profiles.

Options:
  -m, --max-profiles INTEGER  Maximum number of profiles to evaluate.
                              [default: 20]
  --help                      Show this message and exit.
```

### Outreach: `outreach`

The `outreach` command sends connection requests or first messages to qualified leads. For connection requests, it will send the `connect_message` specified in the campaign. If no connect message is specified, **it will not send** the connection request. The `first_message` is sent if the qualified profile is already connected. If no first message is specified, **it will not send** anything.

There are daily and weekly message quotas, so please be mindful not to breach those limits. You can control how many connect and first messages you send using the flags below.

```bash
linkiq outreach --help
Usage: linkiq outreach [OPTIONS]

  Send messages to qualified leads

Options:
  -c, --max-connect-request INTEGER
                                  Maximum connect requests to send. Max is 10
                                  [default: 10]
  -m, --max-first-message INTEGER
                                  Maximum first messages to send. Max is 10
                                  [default: 10]
  --help                          Show this message and exit.
```

### Dashboard: `view`

There is a lightweight dashboard to view leads and browse through them. You can launch this using the `view` command. It's best to let this run in the background.

```bash
linkiq view & 
```

### Automated Scheduling: `scheduler`

All of the above commands can be run on "autopilot" schedule. The `scheduler` will run the gathering, qualifying, and outreach tasks in the background.

```bash
linkiq scheduler --help
Usage: linkiq scheduler [OPTIONS]

  Run only the scheduler.

Options:
  --help  Show this message and exit.
```

### Combined Mode: `run`

You can run the tasks on schedule and launch the dashboard simultaneously with a single `run` command.

```bash
linkiq run --help
Usage: linkiq run [OPTIONS]

  Run both background scheduler and UI.

Options:
  --help  Show this message and exit.
```