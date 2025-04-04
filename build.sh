set -o errexit

pip install -requirements.txt
pip manage.py collectstatic --noinput
pip manage.py migrate