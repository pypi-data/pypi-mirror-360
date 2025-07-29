# You Cant Change That! (YCCT)

## About

You Cant Change That! Stop breaking things! YCCT is a service that monitors the permissions, attributes and content of files to prevent system damage, such as someone accidentally chmod/chowning `/etc`!

### How does it work?

YCCT Creates a thread for each monitored item, periodically checking its state, and comparing it to the previously known one. When a change is detected, the item's permissions/attributes/content are restored. Items can be a file or directory, and each can be monitored differently. CLI Commands are called through a local socket to the service to configure and manage YCCT.

At start, any monitored items are delayed 0.1 seconds between each start. Additionally, each thread gains up to `monitor_interval` seconds of offset for its check, randomly generated for each thread, to prevent huge cpu spikes and many threads competing for activity. For example, with `monitor_interval=5` (default), a check for any given item will occur every 5-10 seconds.

## Usage

YCCT is a commandline only service.

To Start monitoring an item run:
 - `ycct monitor -f /path/to/file -t perms`, You can specify `-t perms attr content` (and variations of it) to monitor different aspects of the file.

Once monitored, YCCT will periodically check the state of the file against the state it found when the file was added. If the state changes, it will be logged, and then restored.

To temporarily disable monitoring of an item, you can run:
 - `ycct disable -f /path/to/file`

Once disabled, changes to the file will not be met with a restore. This allows for changes to be made, even temporarily.

Items can also be re-enabled by:
 - `ycct enable -f /path/to/file`

Items can be removed completely as well:
 - `ycct remove -f /path/to/file`

The State DB can be updated by running a rescan:
 - `ycct scan`

Scans will purge the entire State DB, and cause all items to be rescanned for their state. Items which are disabled will not get their state updated until they are enabled again.

If you wish to permanently change the state of an item:

 1. Disable the item
 2. Modify the item's state, content, etc
 3. Execute a re-`scan`
 4. Enable the item

You may additionally check the status of the serice by running:
 - `ycct status`

This will output the number of items monitored, enabled/disabled items, and what type of monitoring is occuring for each

### Commands and API

Information about CLI Commands or the API / Client Library can be found [here](COMMANDS.md)

## Configuration

| Option           | Default                | Description                                                                       |
|------------------|------------------------|-----------------------------------------------------------------------------------|
| scandb           | /var/lib/ycct/ycct.db  | Scanner / Monitoring Database, what files are monitored, etc                      |
| statedb          | /var/lib/ycct/state.db | File/Directory State Database, State of each file/directory                       |
| content_dir      | /var/lib/ycct/content  | Directory where saved-state Content is stored, when content enabled               |
| monitor_interval | 5                      | Delay between monitoring state checks                                             |
| enable_wall      | True                   | Enable alerting via `wall` when a file changes or a content-changed restore fails |

## Setup

This service should be run as root, to ensure that permissions and attributes can be managed, without the need for sudo. While I am generally against this practice, this is the best method for this utility.

### Setup Steps

 1. Create directories:
    1. `/etc/ycct/` - Configuration
    2. `/var/run/ycct/` - Socket
    3. `/var/lib/ycct/` - State / Monitoring DBs
 2. Create a config File at `/etc/ycct/ycct.toml` (YAML and JSON may also be used, if you so wish)
 3. [optional] Create a service file (provided in `src/ycct/ycct.service`)
    1. Must replace `%EXECPATH%` with the path where ycct lives
 4. [optional] Enable the service
 5. Start the service

## Notes

### Content Monitoring
 - Content Monitoring should not be done for large files unless absolutely neccessary. YCCT Reads the file as binary, and generates an SHA256 of the file, this is done for the state update, as well as the periodic monitoring checks. As a result, monitoring the content of large files may bog down your system.
 - Content Restoration may fail if the expected SHA256 of the restoration file does not match what the state DB thinks the hash should be. In this case, restore will halt, and a message will be logged. Monitoring of this file will be disabled as well, to prevent log spamming and further damage.

### Attribute Monitoring
 - Not all attributes are available on all systems. The ones provided by the `getfattr` and `setfattr` functions were pulled from my current manpages. Attributes that arent available will be masked, but you may see messages about unsupported attributes. These are to be expected.
   - These functions additionally execute a single `chattr` command for each attribute, in order to ensure the highest possible potential for successfully setting / unsetting attributes. Using a single long command of them tends to not work well and results in the command failing.

### Directory Monitoring
 - When a directory is monitored recursively, any new files will additionally be added to monitoring automatically.
 - To disable a single file within a directory, you must add it individually, and then disable it, such as the example below
     ```
     ycct monitor -f /etc -t perms attr
     ycct monitor -f /etc/crontab -t perms attr # Type does not matter or need to match top directory
     ycct disable -f /etc/crontab
     ``` 
 - A Recursively monitored directory cannot be easily removed, each file must be individually removed unfortunately.

### Scanning
- `scan` operations purge the entire State DB, and causes a reload of all item states. As a result, there is a very brief window where an item may change, and the state will update to that instead. Steps should be taken to ensure no operations are occuring on the monitored items before running a scan
 