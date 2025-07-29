"""Tricks `pip` into installing packages from local directories and extracts requirements.

Functions:
	- `installPackageTarget`: Tries to trick `pip` into installing the package from a given directory.
	- `makeListRequirementsFromRequirementsFile`: Reads a requirements.txt file, discards anything it couldn't understand, and creates a `list` of packages.

Usage:
	from pipAnything import installPackageTarget
	installPackageTarget('path/to/packageTarget')

	`pip` will attempt to install requirements.txt, but don't rely on dependencies being installed.

"""

from packaging.requirements import Requirement
from typing import TYPE_CHECKING
from Z0Z_tools.filesystemToolkit import findRelativePath
import os
import pathlib
import subprocess
import sys
import tempfile

if TYPE_CHECKING:
	from io import TextIOWrapper

def makeListRequirementsFromRequirementsFile(*pathFilenames: str | os.PathLike[str]) -> list[str]:
	"""Read one or more requirements files and extract valid package requirements.

	Parameters
	----------
	*pathFilenames : str | os.PathLike[str]
		(path2filenames) One or more paths to requirements files.

	Returns
	-------
	listRequirements : list[str]
		(list2requirements) A `list` of unique, valid package requirements found in the provided files.

	"""
	listRequirements: list[str] = []

	for pathFilename in pathFilenames:
		readStream: TextIOWrapper | None = None
		if pathlib.Path(pathFilename).exists():
			try:
				# NOTE Context managers often cause new problems in this specialty case.
				readStream = open(pathFilename)  # noqa: PTH123, SIM115
				for commentedLine in readStream:
					sanitizedLine: str = commentedLine.split('#')[0].strip()  # Remove comments and trim whitespace

					if not sanitizedLine:
						continue

					try:
						Requirement(sanitizedLine)
						listRequirements.append(sanitizedLine)
					except Exception:  # noqa: BLE001, S110
						pass
			finally:
				if readStream:
					readStream.close()

	return sorted(set(listRequirements))

def make_setupDOTpy(relativePathPackage: str | os.PathLike[str], listRequirements: list[str]) -> str:
	"""Generate setup.py file content for installing the package.

	Parameters
	----------
	relativePathPackage : str | os.PathLike[str]
		(relative2path2package) The relative path to the package directory.
	listRequirements : list[str]
		(list2requirements) A `list` of requirements to be included in install_requires.

	Returns
	-------
	setupDOTpy : str
		(setup2dot2py) The setup.py content to be written to a file.

	"""
	return rf"""
import os
from setuptools import setup, find_packages

setup(
	name='{pathlib.Path(relativePathPackage).name}',
	version='0.0.0',
	packages=find_packages(where=r'{relativePathPackage}'),
	package_dir={{'': r'{relativePathPackage}'}},
	install_requires={listRequirements},
	include_package_data=True,
)
"""

def installPackageTarget(pathPackageTarget: str | os.PathLike[str]) -> None:
	"""Install a package by creating a temporary setup.py and tricking `pip` into installing it.

	Parameters
	----------
	pathPackageTarget : str | os.PathLike[str]
		(path2package2target) The directory path of the package to be installed.

	"""
	filenameRequirementsHARDCODED = pathlib.Path('requirements.txt')
	filenameRequirements = pathlib.Path(filenameRequirementsHARDCODED)

	pathPackage: pathlib.Path = pathlib.Path(pathPackageTarget).resolve()
	pathSystemTemporary = pathlib.Path(tempfile.mkdtemp())
	pathFilename_setupDOTpy: pathlib.Path = pathSystemTemporary / 'setup.py'

	pathFilenameRequirements: pathlib.Path = pathPackage / filenameRequirements
	listRequirements: list[str] = makeListRequirementsFromRequirementsFile(pathFilenameRequirements)

	# Try-finally block for file handling: with-as doesn't always work  # noqa: ERA001
	writeStream: TextIOWrapper | None = None
	try:
		writeStream = pathFilename_setupDOTpy.open(mode='w')
		relativePathPackage: str = findRelativePath(pathSystemTemporary, pathPackage)
		writeStream.write(make_setupDOTpy(relativePathPackage, listRequirements))
	finally:
		if writeStream:
			writeStream.close()

	subprocessPython = subprocess.Popen(
	# `pip` needs a RELATIVE PATH, not an absolute path, and not a path+filename.
		args=[sys.executable, '-m', 'pip', 'install', str(pathSystemTemporary)],
		stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
	)

	# Output the subprocess stdout in real-time
	if subprocessPython.stdout:
		for lineStdout in subprocessPython.stdout:
			print(lineStdout, end="")  # noqa: T201

	subprocessPython.wait()

	pathFilename_setupDOTpy.unlink()

def everyone_knows_what___main___is() -> None:
	"""Provide a rudimentary CLI for the module.

	Call `installPackageTarget` from other modules.

	"""
	two: int = 2
	packageTarget = sys.argv[1] if len(sys.argv) > 1 else ''
	pathPackageTarget = pathlib.Path(packageTarget)
	if len(sys.argv) != two or not pathPackageTarget.exists() or not pathPackageTarget.is_dir() :
		namespaceModule: str = pathlib.Path(__file__).stem
		namespacePackage: str = pathlib.Path(__file__).parent.stem
		print(f"\n{namespaceModule} says, 'That didn't work. Try again?'\n\n"  # noqa: T201
				f"Usage:\tpython -m {namespacePackage}.{namespaceModule} <packageTarget>\n"
				f"\t<packageTarget> is a path to a directory with Python modules\n"
				f"\tExample: python -m {namespacePackage}.{namespaceModule} '{pathlib.PurePath('path' ,'to', 'Z0Z_tools')}'")
		# What is `-m`? Obviously, `-m` creates a namespace for the module, which is obviously necessary, except when it isn't.
		sys.exit(1)

	installPackageTarget(pathPackageTarget)
	print(f"\n{pathlib.Path(__file__).stem} finished trying to trick pip into installing {pathPackageTarget.name}. Did it work?")  # noqa: T201

def readability_counts() -> None:
	"""Bring the snark.

	(AI generated docstring)

	"""
	everyone_knows_what___main___is()

def main() -> None:
	"""Install package from working directory using pip.

	(AI generated docstring)

	Executes the main workflow to install packages from the current working
	directory by creating temporary files and utilizing pip's installation
	mechanisms.

	"""
	readability_counts()

if __name__ == "__main__":
	main()
