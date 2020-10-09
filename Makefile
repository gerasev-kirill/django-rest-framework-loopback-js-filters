install_virtualenv:
	rm -fr .virtualenv/p2 || true
	virtualenv --python=/usr/bin/python2.7 .virtualenv/p2
	chmod +x .virtualenv/p2/bin/activate
	ln -s .virtualenv/p2/bin/activate ap2 || true
	bash -c "source ap2; pip2 install -r ./requirements.django.txt"

install_virtualenv3:
	rm -fr .virtualenv/p3 || true
	virtualenv .virtualenv/p3
	chmod +x .virtualenv/p3/bin/activate
	ln -s .virtualenv/p3/bin/activate ap3 || true
	bash -c "source ap3; pip3 install wheel; pip3 install -r ./requirements.django.txt"

install_virtualenv4:
	rm -fr .virtualenv/p4 || true
	virtualenv .virtualenv/p4
	chmod +x .virtualenv/p4/bin/activate
	ln -s .virtualenv/p4/bin/activate ap4 || true
	bash -c "source ap4; pip3 install wheel; pip3 install -r ./requirements.django-3.8.txt"

run_tests:
	bash -c "source ap2; python2 ./manage.py test tests"

run_tests3:
	bash -c "source ap3; python3 ./manage.py test tests"

run_tests4:
	bash -c "source ap4; python3 ./manage.py test tests"
