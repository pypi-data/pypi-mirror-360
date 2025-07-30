## Installation
set PYTHONPATH=src
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
python setup.py sdist bdist_wheel
twine upload dist/*