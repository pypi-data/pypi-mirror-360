# Vibe Farm

Vibe Farm lets you write normal Python modules that have missing
implementations. Mark any function with the :func:`vibe_farm.farm` decorator and
raise :class:`vibe_farm.code` inside the body. The compiler reads those `.py`
files and generates corresponding `.vibe.py` modules containing the actual
implementation. At runtime, :func:`farm` hot swaps the definitions with their
generated counterparts if present.

The project is designed to run inside a devcontainer, but the CLI works on any
Python 3.12+ environment.

## Quick Start

Install the package (the OpenAI and Anthropic client libraries are installed as
dependencies) and compile a Python file that uses :func:`farm`:

```bash
pip install vibe-farm
vibe_farm compile examples/hello_world/hello_world.py
```

The resulting `.vibe.py` module will appear alongside the source file.

## Design Decisions

Why `@farm` and `raise code()`? An early decision in the exploration is a desire for a few outcomes in the client code:

1. Make the client script directly executable. By decorating, we can hot swap with an LLM-generated implementation at runtime.
2. By raising an exception that extends `NotImplementedError`, the original scripts will still type check "correctly" in IDEs and with static tools such as `mypy`.

## Project Standards & Contribution Guide

### Getting Started
1. **Fork the repository** and clone your fork
2. **Open in a devcontainer** (recommended for consistent tooling)
3. **Wait for the devcontainer to finish setup** - all dependencies are installed automatically
4. **Create a feature branch**: `git checkout -b feature/your-feature-name`
5. **Make your changes** following the development practices below

### Development Environment
- **Devcontainer Ready**: The project includes a complete devcontainer setup with all tools pre-configured
- **Virtual Environment**: Automatically activated in the terminal (`pytest` command works directly)
- **Pre-configured Tools**: Python 3.12+, Poetry, nox, mypy, black, pytest

### Development Workflow

#### Making Changes
1. **Write tests first** - we maintain 100% test coverage
2. **Format your code**: Code is automatically formatted on save, or run `black .`
3. **Run quality checks locally**:
   ```bash
   nox -s lint    # Type checking with mypy + black formatting check
   nox -s tests   # Run full test suite with coverage
   nox            # Run all sessions (tests + lint for all Python versions)
   ```
4. **Commit with conventional commit format**:
   ```bash
   git commit -m "feat: add new feature description"
   git commit -m "fix: resolve issue with component"
   git commit -m "docs: update API documentation"
   ```

#### Commit Message Format
We use [Conventional Commits](https://www.conventionalcommits.org/). Valid types:
- `feat:` - New features
- `fix:` - Bug fixes  
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks
- `ci:` - CI/CD changes
- `build:` - Build system changes

#### Pull Request Process
1. **Push your branch** to your fork
2. **Open a Pull Request** against the `main` branch
3. **PR Title**: Must follow conventional commit format (e.g., "feat: add new compiler feature")
4. **Automated Checks**: The following will run automatically:
   - **CI Tests**: Full test suite on Python 3.12
   - **Code Quality**: mypy type checking and black formatting validation
   - **Security**: Dependency vulnerability scanning
   - **Coverage**: Must maintain 100% test coverage
   - **PR Validation**: Title and commit message format checking

### Continuous Integration

#### Automated Testing
Every pull request and push to `main` triggers:
- **Multi-Python Testing**: Tests run on Python 3.12
- **Full Test Suite**: All unit and integration tests via nox
- **Code Quality Checks**: mypy type checking and black formatting
- **Security Scanning**: Automated dependency vulnerability checks
- **Coverage Reporting**: Results uploaded to Codecov

#### Required Checks
Before merging, all PRs must pass:
- ✅ Tests pass on both Python versions
- ✅ 100% test coverage maintained
- ✅ No mypy type errors
- ✅ Code formatted with black
- ✅ No security vulnerabilities
- ✅ Conventional commit format
- ✅ Code review approved

### Release Process

#### Automated Releases
Releases are automated via GitHub Actions:

1. **Create a version tag**:
   ```bash
   git tag v1.2.3
   git push origin v1.2.3
   ```

2. **Automatic workflow**:
   - Full test suite runs on both Python versions
   - Package is built with Poetry
   - Automatically published to PyPI
   - GitHub Release is created

#### Version Management
- Update version in `pyproject.toml` before tagging
- Follow [Semantic Versioning](https://semver.org/)
- Tag format: `v1.2.3` (with 'v' prefix)

### Maintenance

#### Automated Updates
- **Dependabot**: Automatically creates PRs for dependency updates weekly
- **Scheduled Tests**: Full test suite runs daily to catch integration issues
- **Security Monitoring**: Automated scanning for known vulnerabilities

#### Manual Tasks
- Review and merge Dependabot PRs
- Update Python version support as needed
- Maintain documentation and examples

### Tooling
- **Python 3.12+** (managed by devcontainer)
- **Poetry** for dependency management and packaging
- **pytest** for testing
- **pytest-cov** for coverage
- **mypy** for static type checking
- **black** for code formatting
- **nox** for automation of test and lint tasks
- **ESLint, Node, npm** (available in devcontainer for JS/Node interop if needed)

### Development Practices
- **100% Test Coverage**: All code must be covered by tests
- **Type Safety**: Use modern type hints for all public APIs
- **Code Quality**: Format with black, validate with mypy
- **Documentation**: Document public APIs and complex logic
- **Conventional Commits**: Required for all commits and PR titles

### Local Development Commands
```bash
# Format code (done automatically on save in devcontainer)
black .

# Run type checking and formatting validation
nox -s lint

# Run tests with coverage (must maintain 100%)
nox -s tests

# Run everything (tests + lint for all Python versions)
nox

# Run specific Python version
nox -s tests-3.12
nox -s lint-3.12
```

### Testing Requirements
- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test CLI commands and workflows  
- **Coverage**: Must maintain 100% - no exceptions
- **Mock External Services**: Use mocks for OpenAI/Anthropic APIs
- **Fast Execution**: Tests should complete quickly for CI

### Code Style
- **Formatting**: Black with default settings (line length 88)
- **Type Hints**: Required for all function signatures
- **Imports**: Organized and minimal
- **Documentation**: Docstrings for public APIs using Google style

### Running Tests & Linting
```bash
black .           # Format code
nox -s lint       # Type checking and lint
nox -s tests      # Run unit tests with coverage
nox               # Run all automation sessions
```

### CLI Usage

Vibe Farm provides a small CLI with two main commands:

```bash
vibe_farm compile path/to/file.py   # generate a .vibe.py implementation
vibe_farm analyze path/to/module.py  # inspect code for vibe placeholders
```

Run `vibe_farm --help` for a full list of options.

### Environment Variables

Vibe Farm automatically loads variables from a `.env` file if present. Set the
following keys for each supported provider:

```bash
# OpenAI
OPENAI_API_KEY=your-openai-key
# Anthropic Claude
ANTHROPIC_API_KEY=your-anthropic-key
```

Keep the `.env` file outside version control (it's ignored by `.gitignore`).

### License

This project is distributed under the [MIT License](LICENSE).

### Publishing
- Update version in `pyproject.toml`
- Build and publish with Poetry:
  ```bash
  poetry build
  poetry publish
  ```

---
For more details, see the code and comments, or open an issue/discussion!
