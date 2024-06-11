# Developing

The client can be set up in development, which will perform all API calls against the test server of modelevaluation.org and enable more rapid testing.

To switch the client into dev mode, do the following.

## 1. Set environment variables

```shell
export MEORG_BASE_URL_DEV="URLHERE"
export MEORG_DEV_MODE=1
```

It can be useful to run this in a script prior to starting development work.

## 2. Create a credentials file

Run the following command.

```shell
meorg initialise --dev
```

And follow the prompts to connect to the test server and prepare your development credentials file.

Any API calls from now will use the test server, to switch it back run the following command:

```shell
export MEORG_DEV_MODE=0
```

Or remove the environment variable entirely as per your OS.