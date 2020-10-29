#  ADAM Python SDK and Jupyter notebooks

[![Python package](https://github.com/B612-Asteroid-Institute/adam_home/workflows/Python%20package/badge.svg)](https://github.com/B612-Asteroid-Institute/adam_home/actions?query=workflow%3A%22Python+package%22)
[![Coverage Status](https://coveralls.io/repos/github/B612-Asteroid-Institute/adam/badge.svg?branch=master)](https://coveralls.io/github/B612-Asteroid-Institute/adam?branch=master)

This repo contains the Python SDK (software development kit) and Jupyter notebooks for interacting with ADAM (Asteroid Decision, Analysis, and Mapping) API programmatically.

## Configuration

Use the `adamctl` tool to configure your ADAM token and workspace before you run notebooks. The configuration steps usually only need to be done once per ADAM server environment.

### Mac/Linux/WSL

There are 2 required configuration IDs you'll need:

  * Your login token, which you can get using the commands below (Google account required for login)
  * A workspace ID (ask Carise or John for this). The workspace is like a folder for the jobs you submit to ADAM.

```bash
# grab the latest release of adam sdk
conda install -c asteroid-institute adam

# log in with Google account, defaults to prod server
adamctl login

# set your ADAM server configuration's workspace ID
adamctl config envs.prod.workspace "YOUR_WORKSPACE_ID"
```

To view your ADAM server configurations:

```bash
adamctl config
```

## Other configurations

Sometimes you might need to use the ADAM `dev` server (e.g. for experimental APIs). Create a separate ADAM configuration for that workspace.

```
# log into the 'dev' environment
adamctl login dev https://adam-dev-193118.appspot.com/_ah/api/adam/v1

# set your workspace ID
adamctl config envs.dev.workspace "YOUR_WORKSPACE_ID"
```

## Installing ADAM SDK from source

Installing `adamctl` from source, instead of Anaconda. Do this if you're developing the Python SDK.

```bash
# grab the source code
git clone git@github.com:B612-Asteroid-Institute/adam_home
cd adam_home

# create a new conda environment with the necessary dev tools
conda create -n adam-dev --file conda-requirements.txt
conda activate adam-dev

# install ADAM in dev mode
python setup.py develop
```

## ADAM demos

Once you have the package installed, you should be able to run the demonstration
notebooks found in the [demos/](demos/) directory. The [single_run_demo](demos/single_run_demo.ipynb)
is a good place to start.

Before invoking code from the ADAM SDK, you'll want to include the following code at the top of your notebook (after the imports):

```python
# Use the default configuration, which is the prod server
config = ConfigManager().get_config()

# If you need to use a different server e.g. dev:
# config = ConfigManager().get_config('dev')

# Configure the REST API server endpoint and user token
auth_rest = AuthenticatingRestProxy(RestRequests(config['url']), config['token'])
```

See the [single_run_demo](demos/single_run_demo.ipynb) notebook for an example.

## SDK documentation

https://b612-asteroid-institute.github.io/adam_home/index.html

## Developing ADAM

The ADAM SDK is a pure-python package that follows the [standard
setuptools directory](https://python-packaging.readthedocs.io/en/latest/minimal.html) layout and installation mechanisms.
The source code is in the [adam/](adam/) subdirectory, the tests are in
[adam/tests/](adam/tests/). A number of demo notebooks are provided in [demos/](demos/). Conda
package recipe files are in [recipe/](recipe/). [`setup.py`](setup.py) in the root of the
repository handles the install, as well as the creation of the [`setupctl`
script via an
entrypoint](https://setuptools.readthedocs.io/en/latest/setuptools.html#automatic-script-creation).

A typical development loop will consist of:

  * Create a separate Anaconda environment.
  * Running `python setup.py develop`, to add the source code onto your
    `$PYTHONPATH`. This is needed only once.
  * Making some changes to the package in `adam/`
  * Testing with `pytest adam --cov=adam --ignore=adam/tests/integration_tests`
  * Commit, push, PR.
