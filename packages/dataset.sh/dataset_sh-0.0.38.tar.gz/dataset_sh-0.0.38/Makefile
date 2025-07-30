clean:
	rm -f dist/*
	rm src/dataset_sh/server/assets/app-ui.frontend

clean-dist:
	rm -f dist/*

frontend:
	utils/build_frontend.sh

package:
	utils/package.sh
	ls -l dist

upload:
	utils/upload.sh

upload-test:
	utils/upload-test.sh

test:
	coverage run -m pytest --cov=dataset_sh tests; coverage report -m