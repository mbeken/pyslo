code_version=$(python setup.py --version) && \
pip_version=$(yolk -V pyslo | cut -d" " -f2) && \
([ "$code_version" != "$pip_version" ] && twine upload dist/* -u $_PYPI_USERNAME -p $PYPI_PASSWORD || echo "No new version")
