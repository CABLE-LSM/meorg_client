# Contributing

The following outlines the process to contribute to meorg_client.

## 1. Clone the repository

```shell
# Create a work space for repos
mkdir -p $HOME/work

# Move into it
cd $HOME/work

# Clone the repo
git clone git@github.com:CABLE-LSM/meorg_client.git

# Move into it
cd meorg_client
```

## 2. Set up the dev environment

```shell
# Create the development environment
conda env create -f .conda/meorg_client_dev.yaml
```

## 3. Install meorg_client in editable mode

```shell
# Install as editable
pip install -e .
```

You can now edit the source code in your editor of choice and have changes immediately reflected in your environment for rapid development.

Please follow the standard contribution guidelines in addressing issues for the project.