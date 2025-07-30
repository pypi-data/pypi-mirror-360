# CDIAM CLI

This is a repository for CDIAM CLI. .

## Getting Started

To get started with this project, follow these steps:

### From source
1. Clone the repository: `git clone github.com/C-DIAM/cdiam-cli.git`
2. Install: `poetry install` install poetry with https://python-poetry.org/docs/

### From pypip
Run `pip install cdiam-cli` 

### View CLI command
Run `cdiam-cli --help`

## Features

- Save token: `cdiam-cli save-token` must provide server endpoint E.g. https://c-diam.com/api and TOKEN get from CDIAM APP
- Call API: `cdiam-cli call-api <PATH_TO_YAML_OR_JSON_PARAMS>` more detail about params schemas at `<SERVER_ENPOINT>/schemas/docs` E.g. https://c-diam.com/api/schemas/docs



## License

This project is licensed under the [MIT License](LICENSE).
