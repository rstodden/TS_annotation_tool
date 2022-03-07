"""
Specify and load your simplification model here.
"""

import subprocess, os, sys

load_simplification_model = True
simplification_model = "MUSS (Martin et al. (2021))"

if __name__ == '__main__':
	if load_simplification_model:
		if simplification_model == "MUSS (Martin et al. (2021))":
			process = subprocess.Popen(["git", "clone", "https://github.com/facebookresearch/muss.git"], stdout=subprocess.PIPE)
			output = process.communicate()[0]
			os.chdir("muss")
			subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
