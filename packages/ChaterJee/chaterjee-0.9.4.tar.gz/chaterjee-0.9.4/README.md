# ChaterJee

<img src="https://github.com/Pallab-Dutta/ChaterJee/raw/main/ChaterJee/ProfilePhoto.png" alt="ChaterJee" width="200"/>

Often, we need to run computational `trial and error` experiments by just tweaking one or two key parameters. In machine learning, you face similar problems during hyperparameter tuning experiments. 

These are probably the most boring, time-consuming, yet unavoidable phases in our day-to-day research. But what if your experiments could keep working while you're at a date XD ? What if you could kick off a hyperparameter tuning run just before bed — and wake up with results and plots waiting on your phone, like a good morning message from your research? Real-time updates, one-tap reruns, and zero late-night debugging. It’s like having a research assistant in your pocket.

Let me introduce ChaterJee to you — a playful fusion of `Chater`, meaning one who chats, and `Jee`, an honorific used in Indian culture to show respect. Think of `ChaterJee` as the lab assistant you always wanted — one who actually responds, never crashes your code, doesn't ask for co-authorship, and definitely doesn't need coffee all the time, unlike you.

# Installation
As a prerequisite you are required to install the `jq` library for reading JSON files from bash script. 
```bash
sudo apt update
sudo apt install jq
```

Now, you need two things:
 1. The `ChaterJee` module
 2. A telegram BOT that you own

## Installing the module
I recommend to install `ChaterJee` module inside your project's conda environment for a seamless experience. 
```bash
conda activate yourenv
pip install ChaterJee
```

## Get your telegram BOT
To use this `ChaterJee`, you'll need a Telegram Bot Token and your Chat ID. Follow these simple steps:

### Create a Bot and Get the Token
- Open Telegram and search for **@BotFather**.
- Start a chat and send the command `/newbot`.
- Follow the prompts: choose a name and a username for your bot.
- Once done, **BotFather** will give you a **bot token** — a long string like `123456789:ABCdefGhiJKlmNoPQRsTuvWXyz`.

### Get Your Chat ID
- Open Telegram and start a chat with your newly created bot by searching its username.
- Send `Hi` (any message) to your bot.
- Open your browser and visit this URL, replacing `YOUR_BOT_TOKEN` with your token:
`
https://api.telegram.org/bot{YOUR_BOT_TOKEN}/getUpdates
`

    with the above token, this URL becomes:
`
https://api.telegram.org/bot123456789:ABCdefGhiJKlmNoPQRsTuvWXyz/getUpdates
`
- Look for `"chat":{"id":...}` in the JSON response. This number is your **Chat ID**.


# Quick Start
`ChaterJee` has two components. 
 - `NoteLogs` class: This stores log files, and save project locations for parsing updates.
 - `ChatLogs` class: This reads log files, the last line is sent to you via the BOT. It can also share you final plots that you need for your next rerun.

## The minimal example
This will register your JOB with the given `JOBNAME` and logfiles into a JSON file, `<your home>/.data/JOB_status.json`.

`script.py`
```python
# This is a minimal example

# Your imports
from pathlib import Path
import ChaterJee
import json

# your code here
with open("hyperparams.json","r") as ffr:
    HYPERPARAMS = json.load(ffr)
    # get your parameters
    JOBNAME = HYPERPARAMS["JOBNAME"]
    LOGDIR = HYPERPARAMS["LOGDIR"]
    LOGFILE = HYPERPARAMS["LOGFILE"]
    LOGIMAGE = HYPERPARAMS["LOGIMAGE"]

notelogs = ChaterJee.NoteLogs()
notelogs.write(
    jobNAME=JOBNAME,
    logDIR=LOGDIR,
    logFILE=LOGFILE,
    logIMAGE=LOGIMAGE
    )

### Your code that generates logs
print(f"{logs}")

### Your code that generates plot
logPath = Path(LOGDIR)
plt.savefig(logPath / LOGIMAGE)
```

The `hyperparams.json` file should look like the following. It must contain the last 4 `{key: value}` pairs to let our BOT access the log results.

`hyperparams.json`
```json
{
    .
    .

    "JOBNAME": "model_2.4",
    "LOGDIR": "./run_2.4",
    "LOGFILE": "outFile.log",
    "LOGIMAGE": "outImage.png"
}
```
Save the following script in your working directory to rerun your tuning experiments quickly. 

`run.sh`
```bash
#!/bin/bash

# Path to hyperparameter file
hyparam_file="hyperparams.json"

# Read values from config.json using jq
stdout_log=$(jq -r '.LOGFILE' "$hyparam_file")
stdout_dir=$(jq -r '.LOGDIR' "$hyparam_file")

# Create log directory
mkdir -p "$stdout_dir"

# Backup the hyperparam file for reference
cp "$hyparam_file" "$stdout_dir/$hyparam_file"

# Run the Python script with redirected logs
nohup python script.py --hyprm "$hyparam_file" > "$stdout_dir/$stdout_log" 2> "$stdout_dir/error.log" &

# Save the PID of the background process
echo $! > "$stdout_dir/job.pid"
```

Also, make a `kill_run.sh` file to kill this job in case you need to.

`kill_run.sh`
```bash
#!/bin/bash
stdout_dir=$(jq -r '.LOGDIR' hyperparams.json)

# Check if the PID file exists
pid_file="$stdout_dir/job.pid"

if [ -f "$pid_file" ]; then
    pid=$(cat "$pid_file")
    echo "Killing process with PID $pid"
    kill -9 "$pid" && echo "Process killed." || echo "Failed to kill process."
else
    echo "No PID file found. Is the process running?"
fi
```

Next step is to receive updates on your projects. 

`updater.py`
```python
# Run this instance separately to parse job updates
# This is the one which actually communicates with your BOT.

import ChaterJee

if __name__ == '__main__':
    TOKEN = '123456789:ABCdefGhiJKlmNoPQRsTuvWXyz'
    CHATID = '123456789'

    cbot = ChaterJee.ChatLogs(TOKEN, CHATID)
    cbot.cmdTRIGGER()
```
Run the above script in a separate terminal session to start interacting with your BOT.

## At your Telegram App
- Think your inbox as the terminal.
- `cd`, `ls` etc. works as expected. Therefore to go to parent directory, you simply type: `cd ..` , and to list contents type `ls` . You can run the `run.sh` executable just by typing `./run.sh` .
- texts starting with `/` are telegram-BOT commands.

At this stage the following 4 commands work:
- `/start` : Starts the conversation with the BOT.
- `/run` : Runs the job (current directory).
- `/kill` : Kills the job once you allow (current directory).
- `/jobs` : List the jobs as Keyboard button options.
- `/clear` : Clears the chat history once you allow.
- `/edit` : Let you choose and edit a JSON file (from current directory) by the webapp Editor Babu.
- `/edit file.json` : Let you edit and save the JSON file (from any directory) by the webapp Editor Babu. 
