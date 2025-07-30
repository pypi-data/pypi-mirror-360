# `pyglog`

A CLI for Graylog API calls

You must set GRAYLOG_ADDR and GRAYLOG_TOKEN or define them in a .env file.

Example:

GRAYLOG_ADDR=&quot;https://graylog.example.com&quot;

GRAYLOG_TOKEN=&quot;XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX&quot;

**Usage**:

```console
$ pyglog [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `list-sidecars`: List Sidecars
* `list-configurations`: List Sidecar Configurations
* `list-configurations-by-tag`: List Sidecar Configurations associated...
* `list-matching-sidecars`: List Sidecars that contain the search string
* `get-configuration-by-id`: Get details for a configuration by ID.
* `get-configuration-by-tag`: Get details for a configuration by tag name.
* `get-sidecar-by-id`: Get sidecar by ID
* `get-sidecar-details`: Get details for Sidecars that match the...
* `apply-configuration-sidecars`: Apply a Configuration to Sidecars with a...
* `remove-configuration-sidecars`: Remove a Configuration from Sidecars with...

## `pyglog list-sidecars`

List Sidecars

**Usage**:

```console
$ pyglog list-sidecars [OPTIONS]
```

**Options**:

* `-s, --silent`: Silent mode. No output.
* `--help`: Show this message and exit.

## `pyglog list-configurations`

List Sidecar Configurations

**Usage**:

```console
$ pyglog list-configurations [OPTIONS]
```

**Options**:

* `-s, --silent`: Silent mode. No output.
* `--help`: Show this message and exit.

## `pyglog list-configurations-by-tag`

List Sidecar Configurations associated with tag

Arguments:

tag: The name of the tag.

**Usage**:

```console
$ pyglog list-configurations-by-tag [OPTIONS] TAG
```

**Arguments**:

* `TAG`: [required]

**Options**:

* `-s, --silent`: Silent mode. No output.
* `--help`: Show this message and exit.

## `pyglog list-matching-sidecars`

List Sidecars that contain the search string

Arguments:

search_string: A substring that matches one or more sidecar hostnames.

**Usage**:

```console
$ pyglog list-matching-sidecars [OPTIONS] SEARCH_STRING
```

**Arguments**:

* `SEARCH_STRING`: [required]

**Options**:

* `--help`: Show this message and exit.

## `pyglog get-configuration-by-id`

Get details for a configuration by ID.

**Usage**:

```console
$ pyglog get-configuration-by-id [OPTIONS] CONFIGURATION_ID
```

**Arguments**:

* `CONFIGURATION_ID`: [required]

**Options**:

* `-s, --silent`: Silent mode. No output.
* `--help`: Show this message and exit.

## `pyglog get-configuration-by-tag`

Get details for a configuration by tag name.

**Usage**:

```console
$ pyglog get-configuration-by-tag [OPTIONS] CONFIGURATION_TAG
```

**Arguments**:

* `CONFIGURATION_TAG`: [required]

**Options**:

* `-s, --silent`: Silent mode. No output.
* `--help`: Show this message and exit.

## `pyglog get-sidecar-by-id`

Get sidecar by ID

**Usage**:

```console
$ pyglog get-sidecar-by-id [OPTIONS] SIDECAR_ID
```

**Arguments**:

* `SIDECAR_ID`: [required]

**Options**:

* `--help`: Show this message and exit.

## `pyglog get-sidecar-details`

Get details for Sidecars that match the search string

Arguments:

search_string: A string that matches sidecar hostnames.

**Usage**:

```console
$ pyglog get-sidecar-details [OPTIONS] SEARCH_STRING
```

**Arguments**:

* `SEARCH_STRING`: [required]

**Options**:

* `-s, --silent`: Silent mode. No output.
* `--help`: Show this message and exit.

## `pyglog apply-configuration-sidecars`

Apply a Configuration to Sidecars with a hostname that contains the search string.

Arguments:

search_string: A substring that matches one or more sidecar hostnames.

tag_id: The tag used to locate the configuration to be applied

**Usage**:

```console
$ pyglog apply-configuration-sidecars [OPTIONS] SEARCH_STRING TAG_ID
```

**Arguments**:

* `SEARCH_STRING`: [required]
* `TAG_ID`: [required]

**Options**:

* `--no-confirm`: Do not prompt for confirmation.
* `--help`: Show this message and exit.

## `pyglog remove-configuration-sidecars`

Remove a Configuration from Sidecars with a hostname that contains the search string.

Arguments:

search_string: A substring that matches one or more sidecar hostnames.

tag_id: The tag used to locate the configuration to be applied

**Usage**:

```console
$ pyglog remove-configuration-sidecars [OPTIONS] SEARCH_STRING TAG_ID
```

**Arguments**:

* `SEARCH_STRING`: [required]
* `TAG_ID`: [required]

**Options**:

* `--no-confirm`: Do not prompt for confirmation.
* `--help`: Show this message and exit.
