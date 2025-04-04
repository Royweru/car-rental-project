set -o errexit #exit on error

pip install -r requirements.txt
pip manage.py collectstatic --noinput
pip manage.py migrate