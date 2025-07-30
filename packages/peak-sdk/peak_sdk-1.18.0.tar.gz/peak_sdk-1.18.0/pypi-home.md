# Peak SDK

[![PyPI](https://img.shields.io/pypi/v/peak-sdk.svg)](https://pypi.org/project/peak-sdk/)
[![Python Version](https://img.shields.io/pypi/pyversions/peak-sdk)](https://docs.peak.ai/sdk/latest/#platform-support)
[![License](https://img.shields.io/pypi/l/peak-sdk)](https://docs.peak.ai/sdk/latest/license.html)

## What is Peak SDK?

_Peak SDK_ is a Python-based package which can be used to build AI applications in [Peak](https://peak.ai/) Platform. The _Peak SDK_ provides an efficient code-based interface to manage platform resources (Web Apps, Workflows and Images). It also includes an interface to use Press API which can help you efficiently create, manage and deploy Press Applications on the Peak.

## Getting Started

### Setting up a Virtual Environment

To ensure a smooth development experience with _Peak SDK_, we highly recommend creating a Python virtual environment. A virtual environment helps to isolate the dependencies required by your project and prevents conflicts with other projects or the system's global Python environment.

Follow these steps to create a virtual environment using Python's built-in `venv` module:

1. Open a terminal.
2. Navigate to your project's root directory (where you plan to work with the _Peak SDK_).
3. Create a new virtual environment with the following command:

    ```
    python3 -m venv <venv_name>
    ```

4. Activate the virtual environment by running:

    ```
    source <venv_name>/bin/activate
    ```

5. You will now be working within the virtual environment, and you can install dependencies and run the project without affecting other projects on your system's Python environment.

6. When you're finished working on your project, you can deactivate the virtual environment using the following command:

    ```
    deactivate
    ```

### Installation

-   You can install the _Peak SDK_ with the following command using `pip`

    ```shell
    pip install peak-sdk
    ```

    Or if you want to install a specific version

    ```
    pip install peak-sdk==<version>
    ```

-   The _Peak SDK_ ships with the CLI as well. Once CLI is installed, you can enable auto-completion for your shell by running `peak --install-completion ${shell-name}` command, where shell can be one of `[bash|zsh|fish|powershell|pwsh]`.
-   Once this has run, we need to add `compinit` to the shell configuration file (like - .zshrc, .bashrc, etc). To do so, you can the following command
    ```
    echo "compinit" >> ~/.zshrc # replace .zshrc with your shell's configuration file
    ```

### Checking Package Version

-   As mentioned above, the Peak SDK ships with a CLI as well. You can check the version of both the CLI and the SDK quite easily.
-   You can check the version for the `peak-cli` using the following command

    ```bash
    peak --version
    ```

    This should return a response of the following format

    ```bash
    peak-cli==1.18.0
    Python==3.12.3
    System==Darwin(23.6.0)
    ```

-   To check the version of the `peak-sdk`, the following code snippet can be used

    ```python
    import peak

    print(peak.__version__)
    ```

    This should print the version of the SDK

    ```
    1.18.0
    ```

### Using the SDK and CLI

-   To start using the SDK and CLI, you'll need a Personal Access Token (PAT).
-   If you don't have one yet, sign up for an account on the Peak platform to obtain your Personal Access token (PAT).
-   To export it, run the following command in your terminal and replace <peak_auth_token> with your actual PAT:
    ```
    export PEAK_AUTH_TOKEN=<peak_auth_token>
    ```

### Documentation

You can access the documentation for the SDK and CLI at [https://docs.peak.ai/sdk/latest/](https://docs.peak.ai/sdk/latest/).
Here are some quick links to help you navigate easily:

-   [SDK Reference](https://docs.peak.ai/sdk/latest/reference.html)
-   [CLI Reference](https://docs.peak.ai/sdk/latest/cli/reference.html)
-   [Usage](https://docs.peak.ai/sdk/latest/usage.html)
-   [CLI Usage](https://docs.peak.ai/sdk/latest/cli/usage.html)
-   [Migration Guide](https://docs.peak.ai/sdk/latest/migration-guide.html)
-   [FAQ](https://docs.peak.ai/sdk/latest/faq.html)

### Platform Support

  <div class="support-matrix" style="background-color:transparent">
    <div class="supported-versions" style="text-align:center">
      <table class="center-table">
        <caption style="text-align:left">
          <strong>Support across <i>Python versions</i> on major </strong><i>64-bit</i><strong> platforms</strong>
        </caption>
        <!-- table content -->
        <thead>
          <tr>
            <th>Python Version</th>
            <th>Linux</th>
            <th>MacOS</th>
            <th>Windows</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>3.8</td>
            <td>🟢</td>
            <td>🟢</td>
            <td>🟤</td>
          </tr>
          <tr>
            <td>3.9</td>
            <td>🟢</td>
            <td>🟢</td>
            <td>🟤</td>
          </tr>
          <tr>
            <td>3.10</td>
            <td>🟢</td>
            <td>🟢</td>
            <td>🟤</td>
          </tr>
          <tr>
            <td>3.11</td>
            <td>🟢</td>
            <td>🟢</td>
            <td>🟤</td>
          </tr>
          <tr>
            <td>3.12</td>
            <td>🟢</td>
            <td>🟢</td>
            <td>🟤</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="legend">
      <table style="text-align:center">
        <caption style="text-align:left">
          <strong>Legend</strong>
        </caption>
        <thead>
          <tr>
            <th>Key</th>
            <th>Status</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>🟢</td>
            <td>Supported</td>
            <td>regularly tested, and fully supported</td>
          </tr>
          <tr>
            <td>🟡</td>
            <td>Limited Support</td>
            <td>not explicitly tested but should work, and supported on a best-effort basis</td>
          </tr>
          <tr>
            <td>🟤</td>
            <td>Not Tested</td>
            <td>should work, but no guarantees and/or support</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

## More Resources

-   [License](https://docs.peak.ai/sdk/latest/license.html)
-   [Changelog](https://docs.peak.ai/sdk/latest/changelog.html)
