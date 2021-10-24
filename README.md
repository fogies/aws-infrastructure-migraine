# aws-infrastructure-migraine

Infrastructure components for pilot migraine app deployment, including:

- Terraform server infrastructure in `terraform`.
- Application server in `server_flask`.
- Task server in `server_celery`.

## Development Environment

With prerequisites:

- System dependencies installed (as in [Installation of System Dependencies](#installation-of-system-dependencies)).
- Within an activated Pipenv shell (as in [Initializing and Using Pipenv](#initializing-and-using-pipenv)).
- Secrets provided (as in [Providing Secrets](#providing-secrets)).

Pending further development, a typical development environment then:

- Runs a Flask application server locally, with hot reloading.  
- Runs a Celery task server locally, with hot reloading.  

```
  depend.install.all               Install all dependencies.
  dev.flask.serve                  Start Flask, listening on `localhost:4000`, including hot reloading.
  dev.celery.serve                 TODO
```

For now, test the database connection by creating, exercising, and deleting test accounts:

```
  depend.install.all               Install all dependencies.
  database.tests.create-accounts   Create test accounts.
  database.tests.test-accounts     Exercise test accounts by creating and retrieving documents.
  database.tests.delete-accounts   Delete test accounts.
```

### Using Invoke

  This project uses [Invoke](https://www.pyinvoke.org/) for task execution.
  
  ```
  invoke -l
  ```
  
  For example:
  
  ```
  Available tasks:
  
    database.initialize              Initialize the database.
    database.tests.create-accounts   Create test accounts.
    database.tests.delete-accounts   Delete test accounts.
    database.tests.test-accounts     Exercise test accounts by creating and retrieving documents.
    depend.install.all               Install all dependencies.
    depend.install.celery            Install celery dependencies.
    depend.install.flask             Install flask dependencies.
    depend.install.tasks             Install tasks dependencies.
    depend.update.all                Update all dependencies.
    depend.update.celery             Update celery dependencies.
    depend.update.flask              Update flask dependencies.
    depend.update.tasks              Update tasks dependencies.
    dev.flask.serve                  Start Flask, listening on `localhost:4000`, including hot reloading.
    helm.package                     Build packages from charts into staging.
    helm.release                     Release staged packages.
    helmfile.apply                   Apply helmfile/helmfile.yaml in the instance.
    prod.flask.serve                 Start Flask, listening on `0.0.0.0:4000`.
    terraform.ecr.apply              Issue a Terraform apply.
    terraform.ecr.destroy            Issue a Terraform destroy.
    terraform.eip.apply              Issue a Terraform apply.
    terraform.eip.destroy            Issue a Terraform destroy.
    terraform.instance.apply         Issue a Terraform apply.
    terraform.instance.destroy       Issue a Terraform destroy.
    terraform.instance.ip            Public IP of the instance.
    terraform.instance.ssh           Open an SSH session.
  ```

## Installation of System Dependencies

Requires availability of Git and of Python dependencies.

### Git

Requires a Git executable on the path.

- On Windows, development has used [Git for Windows](https://git-scm.com/download/win).

### Python

For Python components, requires Python and the Pipenv package manager.

- [Python](https://www.python.org/)

  Development uses version 3.9.x.

  On Windows, specific versions can be installed: <https://www.python.org/downloads/>
  
  On Mac, specific versions are managed using pyenv: <https://github.com/pyenv/pyenv>
  
- [Pipenv](https://pipenv.pypa.io/en/latest/)

  Pipenv manages creation of a Python virtual environment and pip installation of dependencies in that environment.
    
  Pipenv must be installed in an existing Python installation, typically a global installation:  
    
  ```
  pip install pipenv
  ```
    
  The `pipenv` command is then available in that Python installation. For example:
    
  ```
  pipenv --version
  ```

  or as a module:

  ```
  python -m pipenv --version
  ```
  
  Depending on how a machine manages specific versions of Python, possibilities for accessing Pipenv include:
    
  - On Windows, install a specific version of Python in a known directory.  
    Then use a full path to that installation:
    
    ```
    C:\Python39\Scripts\pip install pipenv
    C:\Python39\Scripts\pipenv --version
    ```  
    
  - On a Mac:
    - Install pyenv using Homebrew or [pyenv-installer](https://github.com/pyenv/pyenv-installer).
    - Install Pipenv in any Python environment, such as the global environment.
    
    Pipenv will detect a Pipfile's desired version of Python and use pyenv to create an appropriate virtual environment.
  
    ```
    pip install pipenv
    pipenv --version
    ```
    
  With Pipenv installed and access to the `pipenv` command, see [Initializing and Using Pipenv](#initializing-and-using-pipenv).

## Initializing and Using Pipenv

Pipenv creates a Python virtual environment that includes the dependencies in a `Pipfile.lock`.
You must first initialize the virtual environment, then activate a shell within the virtual environment.

### Initializing Pipenv

Ensure Pipenv is installed and the `pipenv` command is accessible, as in [Installation of System Dependencies](#installation-of-system-dependencies):

```
pipenv --version
```

Initialize a virtual environment by using the `pipenv` command to install the `Pipfile.lock` dependencies:

```
pipenv sync
```

Then activate a shell inside the created virtual environment.

On Windows:

- The `pipenv shell` implementation has issues (e.g., lacks command history). You may prefer:

  ```
  pipenv run cmd
  ```

- As a convenience, this project includes:

  ```
  pipenv_activate.bat
  ```

- When Pipenv is activated, the `cmd` environment will display `(Pipenv)`:

  ```
  C:\devel\scope-web (Pipenv)>
  ```

On a Mac:

- The default `pipenv shell` works well.

  ```
  pipenv shell
  ```

### Using Pipenv

Within a Pipenv shell, all commands benefit from dependencies in `Pipfile` and `Pipfile.lock`.
See examples in [Development Environment](#development-environment) and in [Using Invoke](#using-invoke).

This project's development dependencies also include Pipenv, 
so the `pipenv` command is available locally (e.g., without a need to reference a specific global installation). 

- To ensure all dependencies are current (i.e., match all `Pipfile.lock`):

  ```
  invoke depend.install.all
  ```

- To install a new dependency, update versions of all dependencies, and update `Pipfile` and `Pipfile.lock`,
  first change into the project directory and then issue use `pipenv install`:

  ```
  cd <directory>
  pipenv install <package>
  cd ..
  ```

- To install a new development dependency, update versions of all dependencies, and update `Pipfile` and `Pipfile.lock`,
  first change into the project directory and then issue use `pipenv install --dev`:

  ```
  cd <directory>
  pipenv install --dev <package>
  cd ..
  ```

## Providing Secrets

Runtime secrets are expected in the `secrets` directory.

Secrets needed for infrastructure configuration are in `secrets/configuration`.

- `secrets/couchdb_config.yaml`

  Secret for configuring CouchDB.

Secrets needed by clients are in `secrets/clients`.

- `secrets/couchdb_client_config.yaml`

  Secret for clients connecting to CouchDB.

Secrets needed for testing are in `secrets/tests`.

- `secrets/accounts_config.yaml`

  Secret for test accounts.
