# Android Publisher

**Usage**:

```console
$ androidpublisher [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `upload`

## `androidpublisher upload`

**Usage**:

```console
$ androidpublisher upload [OPTIONS] PACKAGE_NAME
```

**Arguments**:

* `PACKAGE_NAME`: [required]

**Options**:

* `--aab-file FILE`: [default: app.aab]
* `--track [internal|alpha|beta|production|rollout]`: [default: internal]
* `--json-key FILE`: [default: credential.json]
* `--help`: Show this message and exit.
