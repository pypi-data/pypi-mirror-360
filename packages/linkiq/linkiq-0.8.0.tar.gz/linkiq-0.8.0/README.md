
> Before you use LinkIQ it is critical to read the [LinkedIn User Agreement](https://www.linkedin.com/legal/user-agreement#dos). You are solely responsible for using the software in a manner compliant with LinkedIn terms and conditions.

> Please also read the LinkIQ LICENSE terms and conditions, before proceeding.

# LinkIQ
LinkIQ is a your **personal** LinkedIn Copilot. The intent of this software is to help you automate some of the repetitive tasks such as qualifying a profile as a lead or sending outreach message. 

LinkIQ can do the following
- gather who has viewed your profile or reacted to your posts
- gather the profiles as you conduct search
- qualify these profiles using criteria that you setup (more on this below)
- automatically reach out both for connect request as well as first message

## How to install
The product has been tested on `Mac Sequoia 15.5` and `Python version 3.13.3`. Create a virtual environment so that `linkiq` dependencies don't conflict with what is installed on the system. Then install `linkiq` using `pip install`.

```bash
python3 -m venv venv
source venv/bin/activate
pip install linkiq
playwright install
linkiq --help
```

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

## linkiq commands
### Gather profiles: gather
This command gathers profiles of those who viewed your profile and those who reacted to your posts. The profile viewers are for last 14 days and reactions are for posts from last 7 days. You can select to gather just profile viewers (`-v` flag) or just post reactions (`-p` flag). Default is to gather from both profile views and post reactions. 

```bash
linkiq gather --help
Usage: linkiq gather [OPTIONS]

  Gather LinkedIn data like profile views and post reactions.

Options:
  -v, --profile-views  Gather profile views only.
  -p, --post-reaction  Gather post reactions only.
  --help               Show this message and exit.
  ```

## Search profiles: search
You can gather profiles by conducting specific search.

```bash
linkiq search --help 
Usage: linkiq search [OPTIONS]

  Search and gather LinkedIn profiles.

Options:
  -m, --max-profiles INTEGER  Maximum number of profiles to gather per search
                              round.  [default: 100]
  --help                      Show this message and exit.
```

### Campaign: camp
Campaign lets you define which profiles are of interest. You create a campaign with a name and specify the criteria to qualify the profile. The qualification criteria can be based on:

- `include_keywords`, include profile if any keyword is found in name/title/company of the profile  
- `exclude_keywords`, exclude profile if any of the keyword is found in name/title/company of the profile
If you leave these empty that means any profile is qualified.

For a campaign you can specify the message to send to qualified leads:

- `connect_message`, the message to send along with connection request
- `first_message`, the message to send if the qualified lead is already connected

So your campaign has - name, include/exclude_keywords, and connect/first_message. 

#### camp create
To create campaign

```bash
linkiq camp create
```

### camp list
To list campaigns
```bash
linkiq camp list
```

### camp get 
To get campaign details
```bash
linkiq camp get
```

### Leadgen commands: leadgen
A lead is a profile that is qualified for a specific campaign. **You must have at least one campaign to qualify a profile.**
linkiq will automatically load the profile and based on the provided keywords qualify the lead.

```bash
linkiq leadgen --help
Usage: linkiq leadgen [OPTIONS]

  Search and gather LinkedIn profiles.

Options:
  -m, --max-profiles INTEGER  Maximum number of profiles to evaluate.
                              [default: 20]
  --help                      Show this message and exit.
```

### Outreach: outreach
The `outreach` command send connection request or first message to qualified leads. For connection request, it will send the `connect_message` specified in the campaign. If no connect message is specified **it will not send** the connection request. The `first_message` is sent if the qualified profile is already connected. If no first message is specified **it will not send** anything.

There are daily and weekly message quotas so please be mindful to not breach those. You can control how many connect and first messages you send using the below flags. 

```bash
linkiq outreach --help
Usage: linkiq outreach [OPTIONS]

  Send messages to qualified leads

Options:
  -c, --max-connect-request INTEGER
                                  Maximum connect requests to send. Max is 10
                                  [default: 10]
  -m, --max-first-message INTEGER
                                  Maximum connect requests to send. Max is 10
                                  [default: 10]
  --help                          Show this message and exit.
```

### View: view
There is a lightweight dashboard to see a dashboard of leads and browse the leads. You can launch this using the `view` command. It is best to let this running in a background.

```bash
linkiq view & 
```
### Running all of the above in a schedule: scheduler

All of the above commands can be run on an "autopilot" schedule. The `scheduler` will run the gathering, qualifying, and outreach tasks in background. 

```bash
linkiq scheduler --help
Usage: linkiq scheduler [OPTIONS]

  Run only the scheduler.

Options:
  --help  Show this message and exit.
```

### Scheduler and view both: run
And finally you can run the tasks on schedule and have the viewer launched as well with single `run` command. 

```bash
linkiq run --help
Usage: linkiq run [OPTIONS]

  Run both background scheduler and UI.

Options:
  --help  Show this message and exit.
```