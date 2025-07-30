"""Installs liminal-cli
Currently can be ran on python3.6 and newer
"""
import json
import os
import logging
import logging.config
from pathlib import Path
import re
import sys
import subprocess
import traceback


EMAIL_CONTACT = 'liminal_cl_installer@liminalbios.com'

LIMINAL_DIR = Path.home() / '.liminal-tools'
LIMINAL_DIR.mkdir(exist_ok=True)
LIMINAL_BIN = LIMINAL_DIR / 'bin'
LIMINAL_LOG_DIR = LIMINAL_DIR / 'logs'
INSTALL_LOG_PATH = Path(LIMINAL_LOG_DIR) / 'install-log.txt'
LIMINAL_CLI_NAME = 'liminal_cl'
LIMINAL_PACKAGE_VERSION_TO_INSTALL = os.environ.get('LIMINAL_PACKAGE_FOR_PIP_INSTALL', 'liminal-cli==0.*')
_extra_pip_args = os.environ.get('LIMINAL_INSTALLER_EXTRA_PIP_ARGS', '[]') # allow things like `--pre` or `--index` so we can test pre release
EXTRA_PIP_ARGS = json.loads(_extra_pip_args)
MIN_SUPPORTED_PYTHON_VERSION = (3, 10, 0)
MAX_SUPPORTED_PYTHON_VERSION = (3, 13, 1e9)


def setup_logging() -> logging.Logger:

	LIMINAL_LOG_DIR.mkdir(parents=True, exist_ok=True)

	root_log_config = {
		"version": 1,
		"disable_existing_loggers": False,
		"formatters": {
			# https://docs.python.org/3/library/logging.html#logrecord-attributes
			f"{LIMINAL_CLI_NAME}_basicFormatter": {
				"format": "[%(asctime)s %(levelname)s] - %(message)s",
				"datefmt": "%H:%M:%S",
			},
			f"{LIMINAL_CLI_NAME}_verboseFormatter": {
				"format":
					"[%(asctime)s %(levelname)s %(process)d %(name)s %(filename)s:%(funcName)s:%(lineno)d] - %(message)s",
				"datefmt": "%Y-%m-%dT%H:%M:%S%z",
			},
			f"{LIMINAL_CLI_NAME}_syslogFormatter": {
				"format": "%(levelname)s %(name)s %(filename)s:%(funcName)s:%(lineno)d] - %(message)s"
			}
		},
		"handlers": {
			f"{LIMINAL_CLI_NAME}_consoleHandler": {
				"level": logging.INFO,
				"class": "logging.StreamHandler",
				"formatter": f"{LIMINAL_CLI_NAME}_basicFormatter",
				"stream": sys.stdout,
			},
			f"{LIMINAL_CLI_NAME}_plaintextFileHandler": {
				"level": "DEBUG",
				"class": "logging.handlers.RotatingFileHandler",
				"formatter": f"{LIMINAL_CLI_NAME}_verboseFormatter",
				"filename": INSTALL_LOG_PATH,
				"maxBytes": 5e6, # 5MB
				"backupCount": 5,
			},
			f"{LIMINAL_CLI_NAME}_syslogHandler": {
				"level": logging.INFO,
				"class": "logging.handlers.SysLogHandler",
				"formatter": f"{LIMINAL_CLI_NAME}_syslogFormatter",
			},
		},
		"loggers": {
			LIMINAL_CLI_NAME: {
				"level": "DEBUG",
				"handlers": [f'{LIMINAL_CLI_NAME}_consoleHandler', f'{LIMINAL_CLI_NAME}_plaintextFileHandler', f'{LIMINAL_CLI_NAME}_syslogHandler'],
			},
		},
	}

	logging.config.dictConfig(config=root_log_config)
	return logging.getLogger(LIMINAL_CLI_NAME)
LOGGER = setup_logging()
INSTALL_LOGGER = LOGGER.getChild('standalone_install_wrapper')


def get_python_version_from_executable(executable_path):
	"""
	Runs `executable_path --version` and parses the output, since api (python -m/-c) changes
	Returns a version tuple (major, minor, patch) or None.
	"""
	try:
		process = subprocess.run(
			[executable_path, "--version"],
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			universal_newlines=True,
			timeout=3,
			check=True,
		)
		
		output = (process.stdout.strip() + " " + process.stderr.strip()).strip()
		
		# Regex to find "Python X.Y.Z"
		# Handles optional patch version and potential extra text.
		match = re.search(r"Python\s+(\d+)\.(\d+)(?:\.(\d+))?", output)
		if match:
			major = int(match.group(1))
			minor = int(match.group(2))
			patch = int(match.group(3)) if match.group(3) else 0 # Default patch to 0 if not present

			return (major, minor, patch)
	except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError, OSError):
		pass
	return None


def find_python_executables():
	"""
	Scans PATH for Python 3 executables and returns the path and version tuple for each
	-> dict[str, tuple[int, int, int]]
	"""
	path_env = os.environ.get("PATH", "")
	this_executable_dir = os.path.dirname(sys.executable)
	found_pythons = {}
	directories = path_env.split(os.pathsep) + [this_executable_dir]
	
	# Keep track of real paths to avoid processing symlinks pointing to the same file multiple times
	processed_real_paths = set()

	for directory in directories:
		if not os.path.isdir(directory):
			continue
		try:
			for item_name in os.listdir(directory):
				if item_name.startswith('python'):
					full_path = os.path.join(directory, item_name)
					
					# Ensure it's a file and executable
					if not (os.path.isfile(full_path) and os.access(full_path, os.X_OK)):
						continue

					try:
						real_path = os.path.realpath(full_path)
					except OSError: # If realpath fails (e.g. broken symlink)
						continue
						
					if real_path in processed_real_paths:
						continue
					
					processed_real_paths.add(real_path)
					
					version_tuple = get_python_version_from_executable(real_path)
					if version_tuple:
						# This handles cases where multiple symlinks (e.g., python3, python3.10)
						# point to the same executable. We only store it once by its real_path.
						found_pythons[real_path] = version_tuple

		except OSError: # Permission denied for os.listdir, etc.
			continue
	
	# Sort by version tuple (descending) then by path (lexicographically, as a tie-breaker)
	# Python's tuple comparison works directly: (3,10,1) > (3,9,5) is True
	return sorted(found_pythons.items(), key=lambda item: item[1], reverse=True)




def run_command(cmd: list, output_level=logging.DEBUG, logger=LOGGER, **kwargs):
	logger.debug(f'Running command: {cmd}')
	try:
		task = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True, **kwargs)
	except subprocess.CalledProcessError as e:
		logger.error(f'Error running command: {cmd}')
		logger.info(e.stdout)
		logger.info(e.stderr)
		raise e

	logger.log(output_level, task.stdout)
	logger.log(output_level, task.stderr)

	if task.returncode != 0:
		logger.warning(f'Error running command: {task.returncode}: {cmd}')
	else:
		logger.debug(f'Finished command: {cmd}')


def setup(python_path: Path):
	"""
	creates venv for liminal install. pip install takes care of the rest
	"""
	venv = LIMINAL_DIR / 'venv'


	# if already installed, handoff to upgrader
	try:
		import liminal
		liminal.prompt_upgrade()
		exit()
	except ModuleNotFoundError:
		INSTALL_LOGGER.debug('CLI not installed, continuing')
	except Exception:
		INSTALL_LOGGER.debug('CLI installed, issue prompting upgrade', exc_info=True)

	INSTALL_LOGGER.info('creating venv')
	run_command([python_path, '-m', 'venv', '--upgrade', venv], logger=INSTALL_LOGGER)

	our_python = venv / 'bin/python'
	run_command([our_python, '-m', 'pip', 'install', '--upgrade', 'pip', 'build'], logger=INSTALL_LOGGER)
	INSTALL_LOGGER.info(f'beginning install of {LIMINAL_PACKAGE_VERSION_TO_INSTALL}')
	run_command([our_python, '-m', 'pip', 'install'] + EXTRA_PIP_ARGS + [LIMINAL_PACKAGE_VERSION_TO_INSTALL], logger=INSTALL_LOGGER)
	cli_exec = venv / 'bin' / LIMINAL_CLI_NAME


	installer_command = [cli_exec, 'install']
	INSTALL_LOGGER.debug(f'running {installer_command}')
	task = subprocess.run(installer_command, check=False)
	if task.returncode == 0:
		# so we can have just our custom bin in the users shell profile, and not clutter it with whatever may be in our venv/bin
		run_command(['cp', cli_exec, LIMINAL_BIN], logger=INSTALL_LOGGER)
		INSTALL_LOGGER.debug('finished setup')
	else:
		INSTALL_LOGGER.debug(f'package install command failed: {task.returncode}')
		exit(1)


class PythonRequirementException(Exception):
	pass


def select_valid_python() -> str:
	"""Finds python executables, and selects newest one that we support"""
	python_executables = find_python_executables()

	selected_path = None
	selected_version = None
	for path, version in python_executables:
		if not MIN_SUPPORTED_PYTHON_VERSION <= version <= MAX_SUPPORTED_PYTHON_VERSION:
			continue
		selected_path = path
		selected_version = version
		break

	if selected_path and selected_version:
		version_str = '.'.join(map(str, selected_version))
		INSTALL_LOGGER.info(f'Using {version_str} {selected_path}')
	else:
		INSTALL_LOGGER.info('python_executables=' + json.dumps(python_executables, indent='\t'))
		raise PythonRequirementException(f'Error: No suitable Python 3 installation found. Required python in range [{MIN_SUPPORTED_PYTHON_VERSION}, {MAX_SUPPORTED_PYTHON_VERSION}]')

	return selected_path


def main():
	selected_python = select_valid_python()
	setup(selected_python)


if __name__ == "__main__":
	try:
		main()
	except Exception as e:
		INSTALL_LOGGER.exception('error')
		traceback.print_exc()
		print('\n\n*****There was an error****\n', e)
		print(f'\nPlease copy all the output above and send in an email to {EMAIL_CONTACT}')
		exit(1)
