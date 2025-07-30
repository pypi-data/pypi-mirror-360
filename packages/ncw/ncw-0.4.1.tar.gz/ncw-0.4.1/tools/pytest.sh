python_version=${1:-3.11}
uvx --python ${python_version} --with-editable . --with pytest-cov pytest --cov src --cov tests --cov-precision 2 --cov-report term-missing tests
