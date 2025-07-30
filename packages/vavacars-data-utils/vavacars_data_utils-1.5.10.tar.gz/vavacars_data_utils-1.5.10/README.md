# Vavacars

Vavacars utils library.

## Installation

To use the library, simply install it with pip or add into requirements.txt

```
python3 -m pip install --upgrade vavacars_data_utils
```

## Usage

The library includes a series of common utilities we are using in Vavacars

#### SIQ
- Wrapper to get quotations from SIQ
- Helper_v2 adds querying Redis Cache before asking SmartIQ

#### Camunda DMN
- Wrapper to query Camunda DMN for initial offer (strategies)

#### SQL
- Wrapper to run querys against a MySQL/SQL Server
- SQL Server requires Microsfot OBDC Driver to be installed, for Ubuntu 20.04 use the following comamnds:
```
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list | tee /etc/apt/sources.list.d/msprod.list
apt-get update && ACCEPT_EULA=y DEBIAN_FRONTEND=noninteractive apt-get install -y mssql-tools unixodbc-dev && pip install pymssql
```

#### Azure Helper
- Wrapper to around Azure ML SDK for registering and reploying models

#### BigQuery Helper
- Wrapper to run queries against BigQuery

#### SalesForce Helper
- Wrapper to retrieve data from SalesForce

#### Email
- Wrapper to send emails via Email Communication Resource in Azure

#### Turkey specifics:
- turkish_to_datetime(str): Date conversion from turkish dates

#### Other:
- get_best_match(value, list_values): Find closest string in a list (used for bodytypes, trimlevels, ...)
- deep_get(dictionary, nested_keyss)
- return_on_failure(f,v): Run function f and return v if f yields any exception in other case it will retun f() result
- extract_json_objects(t): Look Json objects in the text t

## Building

First, update at least the version number in setup.cfg

Next, install build package in your environment:

```
python3 -m pip install --upgrade build
```

Then you can run `python3 -m build` to generate the distribution, this will generate the distribution files under dist/ folder. Check the folder as it may contain the files from the previous build.

## Publishing

To publish it we are using twine, so first install it:

```
python3 -m pip install --upgrade twine
```

And then you can publish it running (from this folder), it will ask you for credentials in the registry:

```
twine upload -r pypi dist/*
```

For more details, check:
https://packaging.python.org/en/latest/tutorials/packaging-projects/
