.PHONY: film dry-run validate clean

film:
	python3 pipeline/run_all.py

dry-run:
	python3 pipeline/run_all.py --placeholder

validate:
	cd pipeline && python3 -c "import common; common.load_storyboard(); print('storyboard OK')"

clean:
	rm -rf outputs/.cache outputs/shots outputs/final
