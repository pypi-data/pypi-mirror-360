## Purpose

globsync is a lightweight tool to monitor and manage backups of directories using Globus as backend. Adding directories to globsync's watchlist, will make sure that emails are regularly sent out to the owner to remind them to transfer their data. The email contains instructions on how to use globsync to start the transfer (using Globus flows). This will start the transfer and make sure that globsync is able to monitor the transfer. After the transfer has completed, and if the user has indicated as such, globsync will automatically remove the source. If the source is not removed, globsync will on a regular basis send out emails to the owner to remove their data.

## Current state of supported platforms: beta software

The initial development is focusing on Linux. It may or may not work for you (yet), please use the issue tracker to report on your findings/use cases and more..

## Installation

### Recommended

- check out this repository and cd into it
- run the following commands
```bash
$ python -m venv venv
$ . venv/bin/activate
$ pip install --editable .
```
Afterwards verify the executable `globsync` is available in your PATH

```bash
$ globsync --help
```

### Authentication

Authentication to monitor Globus flows is done using a Globus secret. The secret is to be stored in a file that is only readable by the user. Starting the Globus flow (for the data transfer) for a specific directory will interactively ask for user authentication.


