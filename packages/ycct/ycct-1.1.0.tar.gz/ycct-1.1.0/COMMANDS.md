# YCCT Commands

- [YCCT Commands](#ycct-commands)
  - [Service](#service)
    - [Command: `start`](#command-start)
    - [Command: `stop`](#command-stop)
  - [General](#general)
    - [Command: Server Status (`status`)](#command-server-status-status)
    - [Command: Rescan (`scan`)](#command-rescan-scan)
  - [Monitoring](#monitoring)
    - [Command: `monitor`](#command-monitor)
      - [Arguments](#arguments)
    - [Command: `remove`](#command-remove)
      - [Arguments](#arguments-1)
    - [Command: `enable`](#command-enable)
      - [Arguments](#arguments-2)
    - [Command: `disable`](#command-disable)
      - [Arguments](#arguments-3)

## Service
### Command: `start`
Start YCCT

### Command: `stop`
Stop YCCT

## General
### Command: Server Status (`status`)
Show status of Server, Monitored Files

### Command: Rescan (`scan`)
Force a state scan. Update the state db to the state of all monitored files, as they sit

## Monitoring
### Command: `monitor`
Add a new file to be monitored

#### Arguments
| API Name   | CLI Flag(s)     | Description                                              | Required   | Type   | Default   | Allowed Values                |
|------------|-----------------|----------------------------------------------------------|------------|--------|-----------|-------------------------------|
| file       | --file, -f      | Path of File to monitor                                  | **Y**      | str    | None      |                               |
| type       | --type, -t      | What to Monitor regarding the file specified             | **Y**      | list   | None      | perms, p, content, c, attr, a |
| recursive  | --recursive, -r | If File specified is a directory, recursively monitor it | **N**      | bool   | False     |                               |

### Command: `remove`
Remove a monitored file

#### Arguments
| API Name   | CLI Flag(s)   | Description               | Required   | Type   | Default   |
|------------|---------------|---------------------------|------------|--------|-----------|
| file       | --file, -f    | Path of File to unmonitor | **Y**      | str    | None      |

### Command: `enable`
Re-enable monitoring of a file

#### Arguments
| API Name   | CLI Flag(s)   | Description               | Required   | Type   | Default   |
|------------|---------------|---------------------------|------------|--------|-----------|
| file       | --file, -f    | Path of File to remonitor | **Y**      | str    | None      |

### Command: `disable`
Temporarily disable monitoring of a file

#### Arguments
| API Name   | CLI Flag(s)   | Description                           | Required   | Type   | Default   |
|------------|---------------|---------------------------------------|------------|--------|-----------|
| file       | --file, -f    | Path of File to temporarily unmonitor | **Y**      | str    | None      |
