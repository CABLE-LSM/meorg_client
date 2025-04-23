# Command-Line Usage

The client can be used over the command line in a standard UNIX environment.

> NOTE: The command-line utilities will only work if you have been granted API access by modelevaluation.org.

## Set up credentials.

Credentials to the system are stored in the user home directory `$HOME/.meorg/credentials.json`. To set up credentials follow these steps:

1. Get an account on modelevaluation.org. Take note of the email and password used.
2. Run the command `meorg initialise` on the machine where you have the client installed.
3. Follow the prompts to enter your username and password for modelevaluation.org.

The system will attempt to authenticate with modelevaluation.org, this will write the credentials file upon success. 

> NOTE: This will overwrite any existing credentials.json.

Alternatively, you can create a credentials file at the target filepath manually with a text editor in the following format:

```json
{
    "email": "user@example.com",
    "password": "SuperSecretPassword"
}
```

## Get your Model Output ID

As most of the commands act with respect to a given model output, you must first establish the `$MODEL_OUTPUT_ID` to use.

1. Go to modelevaluation.org.
2. Select "Model Outputs" from the main navigation.
3. Select the appropriate subset (i.e. Owned by Me).
4. Click the appropriate model output.
5. The `$MODEL_OUTPUT_ID` will be displayed in the copy box at the top of the page.

Once credentials are set up and you have your `$MODEL_OUTPUT_ID`, you may use the command-line utilities listed alphabetically below. However, given the asynchronous nature of the server requests, a typical workflow is more useful.

## Typical Workflow

A typical workflow interacting with the server is as follows:

1. Set up your credentials as above.
2. Take note of the `$MODEL_OUTPUT_ID` by visting the appropriate page on modelevaluation.org. For example: ME.org Home > Model Outputs > Owned by me > My Model. The `$MODEL_OUTPUT_ID` will be listed at the top of the page.
3. Upload an output file from your model run (i.e. benchcab), which puts the file in the queue to be transferred to the object store, which can be queried using the returned `$JOB_ID`.
4. Periodically check the status of the transfer using the `$JOB_ID`, acquiring the true `$FILE_ID` upon completion.
5. Attach the transferred file to a `$MODEL_OUTPUT_ID` using its `$FILE_ID`.
6. Once all the desired files are uploaded, transferred and attached, start the analysis. This will return an `$ANALYSIS_ID`, which can be used to query the analysis status.
7. Periodically check the status of the analysis using the `$ANALYSIS_ID` until it returns as complete and prints the URL to the dashboard.

An example script that does this may be as follows:

```shell
#!/bin/bash

FILE_PATH=/path/to/file.nc
MODEL_OUTPUT_ID=abcdef12345

# Upload the file
FILE_ID=$(meorg file upload $FILE_PATH)

# ... some amount of time

# Attach the file to the model output
meorg file attach $FILE_ID $MODEL_OUTPUT_ID

# Start the analysis
ANALYSIS_ID=$(meorg analysis start $MODEL_OUTPUT_ID)

# ... some amount of time

# Check the status of the analysis (inside the loop of your choice)
meorg analysis status $ANALYSIS_ID

# The final command will output the status and URL to the dashboard.
```

## Commands Available

### analysis start

To start an analysis for a given model output using the files provided, execute the following command:

```shell
meorg analysis start $MODEL_OUTPUT_ID
```

Where `$MODEL_OUTPUT_ID` is found on the model output details page in question. Alternatively, copy the last portion of the URL.

For example:
modelevaluation.org/modelOutput/display/**kafS53HgWu2CDXxgC**

This command will return an `$ANALYSIS_ID` upon success which is used in `analysis status`.

### model output create

To create a model output, execute the following command:

```shell
meorg output create $MODEL_PROFILE_ID $EXPERIMENT_ID $MODEL_OUTPUT_NAME
```

Where `$MODEL_PROFILE_ID` and `$EXPERIMENT_ID` are found on the model profile and corresponding experiment details pages on modelevaluation.org. `$MODEL_OUTPUT_NAME` is a unique name for the newly created model output.

This command will return the newly created `$MODEL_OUTPUT_ID` upon success which is used for further analysis. It will also print whether an existing model output record was overwritten.

### model output query

Retrieve Model output details via `$MODEL_OUTPUT_ID`

```shell
meorg output query $MODEL_OUTPUT_ID
```

This command will print the `id` and `name` of the modeloutput. If developer mode is enabled, print the JSON representation for the model output with metadata. An example model output data response would be:

```json
{
    "id": "MnCj3tMzGx3NsuzwS",
    "name": "temp-output",
    "created": "2025-04-04T00:09:44.258Z",
    "modified": "2025-04-17T05:12:08.135Z",
    "stateSelection": "default model initialisation",
    "benchmarks": []
}
```

### analysis status

To query the status of an analysis, execute the following command:

```shell
meorg analysis status $ANALYSIS_ID
```

Where `$ANALYSIS_ID` is the ID returned from `analysis start`.

### file attach

To attach a file to a model output prior to executing an analysis, execute the following command:

```shell
meorg file attach $FILE_ID $MODEL_OUTPUT_$ID
```

Where `$FILE_ID` is the ID returned from `file-status` and `$MODEL_OUTPUT_ID` is the ID of the model output in question.

### file upload

To upload a file to the staging area of the server, execute the following command:

```shell
meorg file upload $PATH
```

Where `$PATH` is the local path to the file.

This command will return a `$FILE_ID` upon success.

### initialise

A simple helper command to write the user credentials file for password-less interaction with the client over the command-line. See above.

### endpoints list

To list all of the available API endpoints, execute the following command:

```shell
meorg endpoints list
```

This command will print a list of endpoints for the API for debugging purposes.