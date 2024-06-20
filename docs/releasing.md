# Releasing

Releases are generated from a stable main as needed to reflect developments and community needs.

Release generation is restricted to project administrators.

Releasing the client involves publishing a tagged release on Github:
1. Go to https://github.com/CABLE-LSM/meorg_client/releases/new
2. Under "Choose a tag", start typing a new release, following SemVer (without leading "v") and click "Create new tag X on publish".
3. Ensure Target is set to "main".
4. Generate release notes if applicable.
5. Enter the tag you set in (2) WITH a leading "v".
6. Edit the release description as needed.
7. Set as the latest release.
8. Click "Publish release".

## Testing the release

To test the release prior to actually releasing the code, you can approximate the build and publication process locally.

```shell
# Move into the repo directory
cd $HOME/work/meorg_client

# Create a build environment
conda env create -n meorg_client_build -f .conda/build_env.yaml

# Activate the environment
conda activate meorg_client_build

# Build the project
conda build .

# If it worked, install the local package
conda install --use-local meorg_client
```

The build should exit immediately upon failure, however, there may be silent errors that can occur, such as no version number on either the pip or conda package (see the logs and look for "None" or "0.0.0" in build artefacts). In this case, there would be a failure in the upload to anaconda.org in the Github Action.

Most users will generally not need to test the build and release process for typical development tasks.