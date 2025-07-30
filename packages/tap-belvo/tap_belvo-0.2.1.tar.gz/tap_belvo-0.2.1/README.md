# tap-belvo

Singer tap for Belvo.

Built with the [Meltano Singer SDK](https://sdk.meltano.com).

## Capabilities

* `catalog`
* `state`
* `discover`
* `about`
* `stream-maps`
* `schema-flattening`

## Settings

| Setting             | Required | Default | Description |
|:--------------------|:--------:|:-------:|:------------|
| secret_id           | True     | None    | Belvo API secret ID. |
| password            | True     | None    | Belvo API password. |
| start_date          | False    | None    | Earliest datetime to get data from |
| base_url            | False    | https://development.belvo.com | Base URL for the Belvo API |
| stream_maps         | False    | None    | Config object for stream maps capability. For more information check out [Stream Maps](https://sdk.meltano.com/en/latest/stream_maps.html). |
| stream_map_config   | False    | None    | User-defined config values to be used within map expressions. |
| flattening_enabled  | False    | None    | 'True' to enable schema flattening and automatically expand nested properties. |
| flattening_max_depth| False    | None    | The max depth to flatten schemas. |

A full list of supported settings and capabilities is available by running: `tap-belvo --about`

### Source Authentication and Authorization

See https://developers.belvo.com/reference/authentication-1.

## Usage

You can easily run `tap-belvo` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-belvo --version
tap-belvo --help
tap-belvo --config CONFIG --discover > ./catalog.json
```

## Developer Resources

### Initialize your Development Environment

```bash
uv tool install --with tox-uv tox
```

### Create and Run Tests

Run all tests:

```bash
tox run-parallel
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Your project comes with a custom `meltano.yml` project file already created. Go ahead and [install Meltano](https://docs.meltano.com/getting-started/installation/) if you haven't already.

1. Install all plugins

   ```bash
   meltano install
   ```

1. Check that the extractor is working properly

   ```bash
   meltano invoke tap-belvo --version
   ```

1. Execute an ELT pipeline

   ```bash
   meltano run tap-belvo target-jsonl
   ```
