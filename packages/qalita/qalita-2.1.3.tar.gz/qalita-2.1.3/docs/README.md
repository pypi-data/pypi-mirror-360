# QALITA Command Line Interface (CLI)

<div style="text-align:center;">
<img width="250px" height="auto" src="https://cloud.platform.qalita.io/logo.svg" style="max-width:250px;"/>
</div>

QALITA Command Line Interface (CLI) is a tool intended to be used by Data Engineers who setup's QALITA Platform's agents, sources and assets.

It gives easy to use command to help them make an up & running qalita platform's environment in no time.

- [QALITA Command Line Interface (CLI)](#qalita-command-line-interface-cli)
- [Quick Start](#quick-start)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Setup](#setup)
    - [Minimal Config](#minimal-config)
    - [Connected Config](#connected-config)
    - [Make an .env file and export ENV Values:](#make-an-env-file-and-export-env-values)
- [qalita agent](#qalita-agent)
  - [qalita agent login](#qalita-agent-login)
  - [qalita agent run](#qalita-agent-run)
    - [Job](#job)
    - [Worker](#worker)
  - [qalita agent joblist](#qalita-agent-joblist)
  - [qalita agent info](#qalita-agent-info)
- [qalita pack](#qalita-pack)
  - [qalita pack init](#qalita-pack-init)
  - [qalita pack list](#qalita-pack-list)
  - [qalita pack run](#qalita-pack-run)
  - [qalita pack validate](#qalita-pack-validate)
  - [qalita pack push](#qalita-pack-push)
- [qalita source](#qalita-source)
  - [qalita source add](#qalita-source-add)
  - [qalita source validate](#qalita-source-validate)
  - [qalita source list](#qalita-source-list)
  - [qalita source push](#qalita-source-push)
- [How to 'Pack' ?](#how-to-pack-)
  - [Init](#init)
  - [At runtime](#at-runtime)
  - [Post runtime](#post-runtime)

# Quick Start

## Installation

As simple as :

```bash
pip install qalita
```

or there is a **Docker Image** available at :

## Usage

If you want to have more detailed and contextual help, type

`qalita COMMAND -h`

```bash
Usage: qalita [OPTIONS] COMMAND [ARGS]...

  QALITA Command Line Interface
```

## Setup

This CLI command communicates with the QALITA Platform API backend.

There are several layers of configuration depending of your needs :

### Minimal Config

- **QALITA_AGENT_NAME**=<agent_name>

The agent will help you identify it in the frontend interface, there are no restrictions on the name.

- **QALITA_AGENT_MODE**=<job/worker>

The mode of the agent :

**Job** : In job mode, when you use the command `qalita agent run`, it will immediately try to run a job on the local current context.

**Worker** : In worker mode, when you use the command `qalita agent run` it will wait for the backend to gives him jobs to run. It is simmilar to a scheduler.

> Note that the command `qalita agent run` needs more configuration to run correctly, it will displays error otherwise.

### Connected Config

- QALITA_AGENT_ENDPOINT=<backend_api_url>

**_Example : http://localhost:3080/api/v1_**

The agent url endpoint gives the ability for the agent to communicate with the qalita's platform endpoints, it enables :

    * Listing packs
    * Running Jobs
    * Publishing sources
    * Publishing packs

- QALITA_AGENT_TOKEN=<api_token>

The token is provided while doing the quickstart steps in the frontend app. It is associated with your user and your role.

> Note that you need to have at least the **[Data Engineer]** role to use the QALITA CLI

### Make an .env file and export ENV Values:

You can alternatively make an .env file and export the values to your environment.

**.env-local**

```bash
QALITA_AGENT_NAME=<agent_name>
QALITA_AGENT_MODE=<job/worker>
QALITA_AGENT_ENDPOINT=https://api.company.com/api/v1
QALITA_AGENT_TOKEN=<api_token>
QALITA_PACK_NAME=<pack_name>
```

Then export the values of the file to ENV values with :

```bash
export $(xargs < .env-local)
```

# qalita agent

The `qalita agent` command allow you to :

- Register an agent to the platform
- Get information about your local agent
- Run a pack on a source
- List agent jobs (past & future)

## qalita agent login

Parameters :

- **name** : the name of the agent
- **mode** : the mode of the agent <job/worker>
- **token** : the api token you get from the platform
- **url** : the backend api url of the platform

`qalita agent login` registers your local agent to the platform, it enables you to run jobs, or create routines (schedules) to run pack programmaticaly.

    You need to have configured your agent with :

    * QALITA_AGENT_ENDPOINT=<backend_api_url>
    * QALITA_AGENT_TOKEN=<api_token>

You can get your token from the frontend or with an OAUTH2 API call to the /users/signin backend's endpoint

More info on your frontend documentation, and on the [Connected config](#connected-config) of the doc

## qalita agent run

Parameters :

- **--name** : the name of the agent
- **--mode** : the mode of the agent <job/worker>
- **--token** : the api token you get from the platform
- **--url** : the backend api url of the platform

Specific parameters in **job** mode :

- **--source** : the source id you want to run your job against
- **--source-version** (optional) : the source version, by default it will run to the latest soruce version
- **--pack** : the pack id you want to run your job against
- **--pack-version** (optional) : the pack version, by default it will run the latest version of the pack

```bash
qalita agent run
```

runs in different mode :

### Job

The agent will run given configuration

- `-p` : a pack_id given with the `qalita pack list`, note that your pack needs to be pushed to the platform in order to have an id.
- `-s` : a source_id given with the `qalita source list`, note that your source needs to be pushed to the platform in order to have an id.

### Worker

The agent will wait until it receives an order from the frontend, it will then worke as same as in job mode.

> Note that this mode will run indefinitely

## qalita agent joblist

Parameters :

- **--name** : the name of the agent
- **--mode** : the mode of the agent <job/worker>
- **--token** : the api token you get from the platform
- **--url** : the backend api url of the platform

List jobs from the platform backend.

## qalita agent info

Parameters :

- **--name** : the name of the agent
- **--mode** : the mode of the agent <job/worker>
- **--token** : the api token you get from the platform
- **--url** : the backend api url of the platform

Get infos about your local agent configuration.

# qalita pack

The `qalita pack` command allow you to :

- Initialize a new pack
- List all available packs
- Validate it
- Run a local pack
- Push your pack version to the platform

## qalita pack init

Parameters :

- **--name** : the name of the pack

Initialize a new pack, you need to have set a **name**, it will create a new **folder** with the name of the pack.

You can set your name by passing a new parameters to the commandline or setting a new environment variable : `QALITA_PACK_NAME=<my-super-pack>`.

Here is the arborescence created :

        ./<pack-name>_pack/
            /run.sh             # Entrypoint file that will be run with qalita agent run
            /README.md          # Documentation file
            /properties.yaml    # Properties file that contains properties about the pack
            /main.py            # (pack specific) The main script (you can run your pack with whatever langage you choose)
            /config.json        # (pack specific) The config file of your pack, you can use it to set any configurations you like.
            /requirements.txt   # (pack specific) The requirements file that is run inside the run.sh

## qalita pack list

Parameters :

- **You need to have logged in with `qalita agent login`**

List all the packs that are accessible to you with the Qalita Platform.

## qalita pack run

Parameters :

- **--name** : Pack name

Run your locally configured pack

## qalita pack validate

Parameters :

- **--name** : Pack name

Validate your locally configured pack

## qalita pack push

Parameters :

- **--name** : Pack name

Push your locally configured pack

# qalita source

The `qalita source` command allow you to :

- Add a new source to your local configuration
- List your local sources from your **qalita-conf.yml** file
- Push your local sources from your **qalita-conf.yml** file
- Validate your conf file **qalita-conf.yml**

> Note , by default the `qalita-conf.yml` file is stored to `~/.qalita/qalita-conf.yml` , set `QALITA_HOME` env to customize the default path.

## qalita source add

This function will help you add a new source to your configuration file `qalita-conf.yaml`

This command doesn't have parameters, you need to follow command prompts.

- **Prompt 1** : Source name
- **Prompt 2** : Source type
- **Prompt 3** : Is conditionnal, depends on the source type.
  - Case : Source Type = `file` : Source path
  - Case : Source Type = `database` : host / port / username / password / database
- **Prompt 4** : Source description
- **Prompt 5** : Is the source a reference ? [bool] (default : false)
- **Prompt 6** : Is the source sensistive ? [bool] (default : false)
- **Prompt 7** : Visibility of the source (private, internal, public) (default : private)

At the end of the prompt, the cli will check reachability of the source depending of the `configuration` and `type`, this step is called `validate_source`

to complete the process of registering a new source to the platform, you need to push your source with the command : `qalita source push`

[![asciicast](https://asciinema.org/a/629618.svg)](https://asciinema.org/a/629618)

## qalita source validate

Helper function to help you add a new source to your configuration file `qalita-conf.yaml`

## qalita source list

Parameters :

You need to have a `qalita-conf.yaml` file that contains your sources configuration.

Exemple :

```yaml
version: 1
sources:
  - config:
      path: /home/user/data_dir
    description: Folder containing csv files
    name: my_csv_files
    owner: user
    reference: false
    visibility: private
    sensitive: false
    type: file
```

In this exemple we have :

**General keys**

| Key     | Type | Description                      |
| ------- | ---- | -------------------------------- |
| version | int  | The version of the configuration |
| sources | list | The list of sources              |

**Source keys**

| Key         | Type   | Description                                            |
| ----------- | ------ | ------------------------------------------------------ |
| name        | string | The name of the source                                 |
| description | string | The description of the source                          |
| owner       | string | The owner of the source                                |
| type        | string | The type of the source                                 |
| config      | dict   | The configuration of the source                        |
| visibility  | string | The visibility of the source <private/internal/public> |
| reference   | bool   | Is the source a reference source                       |
| sensitive   | bool   | Is the source containing sensitive data                |

## qalita source push

Registers your sources to the platform

> Note: If you want to run a pack on your source, you will first need to push your source to the platform. It will give you a source_id with which you can run your pack.

# How to 'Pack' ?

A pack is an entity run by the agent, it can be created by anyone.

**It's purpose is to process the source and retrieve usefull informations about it to feed back into the platform.**

## Init

To create the base pack, see : [qalita pack init](#qalita-pack-init).

## At runtime

The entrypoint of the pack is the `run.sh` file that is located at the **root path** of the temp local folder created by the agent.

**run.sh** Example :

```python
#/bin/bash
python -m pip install --quiet -r requirements.txt
python main.py
```

The pack is feed by a `source_conf.json` file containing the source's `config:` data. This file is located alongside the `run.sh` entrypoint.

**source_conf.json** Example :

```json
{
  "config": {
    "path": "/home/lucas/desktop"
  },
  "description": "Desktop files",
  "id": 1,
  "name": "local_data",
  "owner": "lucas",
  "type": "file",
  "reference": false,
  "sensitive": false,
  "visibility": "private",
  "validate": "valid"
}
```

> Note : The pack is responsible for managing itself it's `source type` compatibility by checking the source **type** in the `source_conf.json` file.

## Post runtime

A the end of the pack run, the agent searchs for :

- `logs.txt` : File uploaded to give feedback logs to the platform in the frontend.

**logs.txt** Example :

```
2023-07-21 11:51:12,688 - qalita.commands.pack - INFO - ------------- Pack Run -------------
2023-07-21 11:51:15,087 - qalita.commands.pack - INFO - CSV files found:
2023-07-21 11:51:15,222 - qalita.commands.pack - ERROR - Summarize dataset:   0%|          | 0/5 [00:00<?, ?it/s]
...
```

- `recommendations.json`

Recommendations file contains the recommendations given by the pack about the source.

**recommendations.json** Example :

```json
{
    [
        {
            "type":"<type of recommendation>",
            "scope":"<scope : is a json>",
            "content":"<any content>"
        },
        {
            ...
        }
        ...
    ]
}
```

- `metrics.json`

Metrics file contains the metrics given by the pack about the source.

**metrics.json** Example :

```json
{
    [
        {
            "scope":"<scope : is a json>",
            "key":"<metric key>",
            "value":"<metric value>"
        },
        {
            ...
        }
        ...
    ]
}
```

Metrics & recommendations are pushed to the platform and are then available to the source's pack run view.
