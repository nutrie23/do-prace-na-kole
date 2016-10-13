from python:3.5

maintainer Automat

run apt-get update
run apt-get install -y build-essential git
run apt-get install -y postgresql-common libpq-dev
run apt-get install -y libtiff5-dev libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk
run apt-get install -y libxml2-dev libxslt-dev
run apt-get install -y node-less yui-compressor
run apt-get install -y libgeos-dev

run mkdir /home/aplikace -p
WORKDIR "/home/aplikace"
copy requirements.txt ./
run pip install six
run pip install -r requirements.txt
copy test_requirements.txt ./
run pip install -r test_requirements.txt

copy . .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
