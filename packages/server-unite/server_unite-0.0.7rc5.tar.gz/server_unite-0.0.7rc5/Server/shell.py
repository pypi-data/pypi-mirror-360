import sys
import pathlib
import subprocess



def Run(command, path=None):

	path = str(pathlib.Path().absolute()) if path is None else path

	process = subprocess.run(
		command,
		shell=True,
		check=True,
		text=True,
		stdout=sys.stdout,
		stderr=sys.stderr,
		cwd=path
	)

	return process.returncode
