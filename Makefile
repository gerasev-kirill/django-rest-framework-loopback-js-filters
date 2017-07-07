install_virtualenv:
	rm -fr .virtualenv/p2 || true
	virtualenv .virtualenv/p2
	chmod +x .virtualenv/p2/bin/activate
	ln -s .virtualenv/p2/bin/activate ap2 || true
	bash ./pip_pkg_install.sh

install_virtualenv3:
	rm -fr .virtualenv/p3 || true
	virtualenv -p python3 .virtualenv/p3
	chmod +x .virtualenv/p3/bin/activate
	ln -s .virtualenv/p3/bin/activate ap3 || true
	bash ./pip_pkg_install3.sh


run_tests:
	bash -c "source ap2; python2 ./manage.py test"

run_tests3:
	bash -c "source ap3; python3 ./manage.py test"
