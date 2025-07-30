# sklearn_nominal
Extra models for scikit-learn, including Decision/Regression Trees with support for nominal values


## Exporting to svg/png/pdf
To export tree graphs to those formats, you need `pygraphviz` (and in the future, possibly other dependencies). To install those dependencies, use:

````
pip install sklearn_nominal[export]
````

Before that, make sure to install `graphviz` (with headers) and `cairo`. In Ubuntu 24.04:

````
sudo apt install libgraphviz-dev graphviz cairosvg 
````


## Developing sklearn_nominal

We use [uv](https://docs.astral.sh/uv/) for project management.

### First run

Install deps:
````
uv sync --dev --extra export
````

Install pre-commit hooks
````
uv run pre-commit install
````

````
uv tool install poethepoet
````

### Running pre commit hooks

````
pre-commit run --all-files
````
### Install PoeThePoet task runner



### Running tests, linter, formatter

````
poe lint
poe format
poe test
````

### Updating docs

````
poe docs
````

### Running benchmarks

````
uv run benchmark/benchmark_openml.py
````


### Publishing to pipy
Via github:
````
#(after pushing a version you want to publish)
git tag v[version]
git push --tags
````
