# Reserve Name

A command-line tool to quickly reserve Python package names on PyPI and Test PyPI.

## Installation

```bash
pip install reserve-name
```

## Usage

After installation, simply run:

```bash
reserve-name
```

The tool will guide you through:

1. **Environment Setup**: On first run, it will help you set up your API tokens and base directory
2. **Package Creation**: Create a UV-based package structure
3. **Publishing**: Upload to both Test PyPI and PyPI
4. **GitHub Integration**: Optionally create a GitHub repository

## Configuration

The tool uses a local `.env` file to store your configuration. You can either:

- Let the tool create it interactively on first run
- Create it manually using the template below

### Environment Variables

Create a `.env` file in your package installation directory with:

```bash
PYPI_API_TOKEN=your_pypi_api_token_here
TEST_PYPI_API_TOKEN=your_test_pypi_api_token_here
BASE_URL=your_base_directory_here
```

### Getting API Tokens

- **PyPI Token**: Get from [https://pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)
- **Test PyPI Token**: Get from [https://test.pypi.org/manage/account/token/](https://test.pypi.org/manage/account/token/)

## Requirements

- Python 3.8+
- `uv` package manager
- `gh` CLI tool (optional, for GitHub repository creation)
- PyPI and Test PyPI accounts with API tokens

## Features

- ✅ Interactive environment setup
- ✅ UV-based package structure
- ✅ Automatic Test PyPI publishing
- ✅ Production PyPI publishing
- ✅ GitHub repository creation
- ✅ Secure token handling
- ✅ Local configuration management

## Security

- API tokens are stored in a local `.env` file with secure permissions
- Tokens are never logged or displayed in output
- The `.env` file is created with read/write permissions for owner only

## License

MIT License