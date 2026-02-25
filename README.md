### Quickfix

Quickfix

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app quickfix
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/quickfix
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade
### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.


### License

mit


A2: 
- Each site config files are used to config each sites. which have their own db host name, password, user name and db type. while the common site config file is used to config basic common things for client and DB for connection and for data caching , ect,. If we break anything from common site config then the whole bench will collapse. and if we accidentally put secret in the common config like secret key. then the secret key is accessible in all sites for bench level.

- web - handles http requests

    worker- handles backround jobs

    scheduler - handles scheduled events

    Socketio - communication

- If a worker stops, the running backgground job will fail and the waiting jobs in the queue will run when the worker start working again.

B1:
- /api/method/quickfix.api.get_job_summary is a whitelist function and api rules are setted in api section v1.py and v2.py then it imported to the handle function in `__init__.py` where frappe route to the page.

- /api/resource/Job Card/JC-2024-0001 it will retrurn the object of the resource mentioned. just like method this also called in app.py -> frappe.api.handle(). difference of these two is one is calling a whitelist fuction and another return the objects ir values.

- /track-job will track the fuction only, in frappe.website.serve.get_response().


- x-frappe-csrf-token - 
08419c8e0a6e395ef4208c91cce2765766eea47c1969da1995082bef. we can find this in networks tab after a POST request. if we ommit this token . there is a validate function named validate_csrf_token in frappe.auth.HTTPRequst it wil return nothing.

- 

