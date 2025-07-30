"""
gets us set up on a server so the users shell history is synced


TODO:
- retry endpoints

future - 
share to shared spot on server
liminal CLI - generate report, get help

errror messages and handling is a little spaghetti



"""

import json
import logging
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import traceback
from uuid import uuid4
import uuid

import requests
import tomlkit

from liminal import config, hack, __version__
from liminal.env import ATUIN_EXEC_PATH, LAST_SUCCESS_INSTALL_FLAG_PATH, Shell, datetime_utcnow, debug, get_os_distro_info
from liminal.standalone_install_wrapper import EMAIL_CONTACT, LIMINAL_BIN, LIMINAL_DIR, LOGGER



LIMINAL_PACKAGE_VERSION = __version__
ATUIN_VERSION = 'v18.6.1'
ATUIN_CONFIG_DIR = Path('~/.config/atuin').expanduser()

LIMINAL_SHELL_EXTENSION = LIMINAL_DIR / 'shell-extension.sh'

USER_INSTALL_KEY_URL = 'https://app.liminalbios.com/users/me/shellsync-install'
USER_LIMINAL_UUID = None
USER_INPUT_INSTALL_TOKEN = os.environ.get('LIMINAL_INSTALL_TOKEN')
SHELL_PROFILE_INFO_URL = 'https://liminalbios.com/'

PROGRESS_TRACKER = {
	# Store progress throughout the script, so we can include in our logs
	# TODO: could replace with a filtered install log
}


def run_command(cmd: list, output_level=logging.DEBUG, logger=LOGGER, **kwargs):
	logger.debug(f'Running command: {cmd}')
	try:
		task = subprocess.run(cmd, capture_output=True, text=True, check=True, **kwargs)
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


class DependencyError(Exception):
	pass

class ExpiredToken(Exception):
	pass

class Server: # SyncAPI
	API_ADDRESS = config.API_ADDRESS
	SYNC_ADDRESS = config.SYNC_ADDRESS

	def verify_sync(self, expected_details):
		LOGGER.debug(f'{expected_details=}')
		payload = {
			'expected_history': expected_details,
			'liminal_user_uuid': USER_LIMINAL_UUID
		}
		resp = requests.post(f'{self.API_ADDRESS}/install/verify-command', json=payload, timeout=10, headers=get_headers())
		self.assert_response_ok(resp)


	def test_connection(self):
		try:
			resp = requests.get(f'{self.API_ADDRESS}/health', timeout=5)
			self.assert_response_ok(resp)
		except Exception as e:
			raise AssertionError(f'Issue connecting to server {self.API_ADDRESS}') from e
		

	def authenticate_user_provided_key(self, install_key: str):
		LOGGER.debug(f'going to verify install token {install_key}')
		resp = requests.get(f'{self.API_ADDRESS}/user/validate', timeout=10, headers=get_headers())
		if resp.status_code == 403 and resp.json()['detail'] == 'Token is expired':
			raise ExpiredToken()


		self.assert_response_ok(resp, error_suffix=f' Invalid token {install_key}')
		PROGRESS_TRACKER['user_is_verified'] = True
		user_id = resp.json()['liminal_user_uuid']
		LOGGER.debug(f'Validated the user id as liminal user {user_id}')
		return user_id


	@classmethod
	def assert_response_ok(cls, response: requests.Response, error_suffix: str = ''):
		assert response.ok, f'Bad Response: {response.url}: {response.status_code} {response.reason}: {response.text}' + error_suffix


def test_environment():
	"""
	assert atuin isn't already installed. exit if it is.
	
	"""
	shell = Shell()
	assert shell.is_supported()
	PROGRESS_TRACKER['shell_is_supported'] = True
	
	if ShellConfig().is_atuin_installed():
		raise RuntimeError("""Atuin is already installed. We currently cant support a custom setup""")
	PROGRESS_TRACKER['atuin_is_not_installed'] = True

	missing_tools = []
	for tool in ['curl', 'sed']:
		try:
			subprocess.run([tool, '--version'], check=True, capture_output=True)
		except (subprocess.CalledProcessError, FileNotFoundError):
			missing_tools.append(tool)
	if missing_tools:
		raise DependencyError(f'Missing the following CLI tools: {missing_tools}')
	PROGRESS_TRACKER['prereq_tools_are_installed'] = True

	Server().test_connection()
	PROGRESS_TRACKER['server_connection_good'] = True



def preflight_tests():
	LOGGER.info('Running preflight checks')
	test_environment()




def dict_factory(cursor, row):
	fields = [column[0] for column in cursor.description]
	return {key: value for key, value in zip(fields, row)}

def test_correctly_setup():
	"""
	- run a command and make sure it syncs, and that the server can decrypt it
	"""
	LOGGER.info('Checking installation')

	command = f'logger "liminal installed {datetime_utcnow()} {uuid4()}"'

	hack.run_login_command(Shell().exec_path, command)

	atuin_db_path = Path('~/.local/share/atuin/history.db').expanduser()
	assert atuin_db_path.exists()
	connection = sqlite3.connect(atuin_db_path.as_posix())
	connection.row_factory = dict_factory
	cursor = connection.cursor()

	count = cursor.execute('SELECT count(id) FROM history').fetchone()
	
	cursor.execute('SELECT * FROM history WHERE command=?', (command,))
	expected_details = cursor.fetchone()
	assert expected_details, f'Test command not found in history. {count=}'
	Server().verify_sync(expected_details)
	PROGRESS_TRACKER['correctly_setup'] = True



class ShellConfig:

	def __init__(self):
		self.shell = Shell()


	def is_atuin_installed(self):
		atuin_is_installed_in_path = False
		try:
			subprocess.run(['atuin', '--help'], check=True)
			atuin_is_installed_in_path = True
		except (subprocess.CalledProcessError, FileNotFoundError):
			pass

		atuin_is_installed_in_home = ATUIN_EXEC_PATH.exists()
		return atuin_is_installed_in_home or atuin_is_installed_in_path


	def generate_extension_file(self):

		shell = Shell()
		LIMINAL_BIN.mkdir(exist_ok=True)
		content = '#!/bin/sh\n# {LIMINAL_PACKAGE_VERSION}'
		# TODO: maybe just include with our package? would be more reliable
		if shell.is_bash():
			commit = 'e8e9024d4d101a69016169e46f5d75df3fdb7e32'
			url = f'https://raw.githubusercontent.com/rcaloras/bash-preexec/{commit}/bash-preexec.sh'
			response = requests.get(url, timeout=10)
			bash_preexec_path = LIMINAL_DIR / 'bash-preexec.sh'
			bash_preexec_path.write_bytes(response.content)
			content += f'\n[[ -f {bash_preexec_path} ]] && source {bash_preexec_path}'

		content += '\n' + f"""
. "$HOME/.atuin/bin/env"
eval "$(atuin init {shell.name})"

# add binaries to PATH if they aren't added yet
# affix colons on either side of $PATH to simplify matching
case ":${{PATH}}:" in
    *:"{LIMINAL_BIN}":*)
        ;;
    *)
        # Prepending path in case a system-installed binary needs to be overridden
        export PATH="{LIMINAL_BIN}:$PATH"
        ;;
esac
		""".strip() + '\n'
		LIMINAL_SHELL_EXTENSION.write_text(content)


	def add(self):
		# TODO: backup their file
		current_content = self.shell.config_file.read_text()
		
		content_to_add = f"""
### Liminal tools ---
# info: Activates liminal shell extension and tools. Managed through `liminal_cl` command. Learn more at {SHELL_PROFILE_INFO_URL}
# version {LIMINAL_PACKAGE_VERSION}. date = {datetime_utcnow()}
. "{LIMINAL_SHELL_EXTENSION}"
sourcing_exit_status=$?
if [ "$sourcing_exit_status" -ne 0 ]; then
	echo "Error: Liminal shell extension not activated"
fi
### --- Liminal tools
		""".strip()

		existing_breadcrumb_pattern = '^### Liminal tools ---.*^### --- Liminal tools'

		if re.search(existing_breadcrumb_pattern, current_content, flags=re.MULTILINE | re.DOTALL):
			updated_file_content = re.sub(existing_breadcrumb_pattern, content_to_add, current_content, flags=re.MULTILINE | re.DOTALL)
		else:
			updated_file_content = current_content + '\n\n' + content_to_add + '\n'
		self.shell.config_file.write_text(updated_file_content)



def uninstall_atuin():
	import shutil
	shutil.rmtree(Path.home() / '.atuin')
	shutil.rmtree(Path.home() / '.local/share/atuin')


def install_atuin():
	LOGGER.info('Installing atuin')
	shellconfig = ShellConfig()
	shellconfig.generate_extension_file()
	shellconfig.add()

	# resp = requests.get(f'https://github.com/atuinsh/atuin/releases/download/{ATUIN_VERSION}/atuin-installer.sh', timeout=10)
	# installer_script = Path('/tmp/atuin-installer.sh')
	# installer_script.write_bytes(resp.content)
	installer_script = Path(__file__).parent / 'atuin-installer.sh'
	env_copy = os.environ.copy()
	env_copy['ATUIN_NO_MODIFY_PATH'] = '1'
	run_command([shellconfig.shell.exec_path, installer_script.as_posix(), '--verbose'], env=env_copy, output_level=logging.INFO)
	
	# atuin's config file isnt created until atuin is ran for the first time
	run_command([shellconfig.shell.exec_path, '-c', f'{ATUIN_EXEC_PATH} info'], env=env_copy, output_level=logging.INFO)
	atuin_config_file = ATUIN_CONFIG_DIR / 'config.toml'
	atuin_config = tomlkit.parse(atuin_config_file.read_text())

	PROGRESS_TRACKER['installed_atuin'] = True

	if not config.LIMINAL_INSTALLER_SKIP_ATUIN_IMPORT_HISTORY:
		# quick hack to at least allow transition for current atuin users 
		# (they can back up their history.db before install, then copy it back and `atuin sync`)
		pass
	else:
		run_command([ATUIN_EXEC_PATH, 'import', 'auto'])

	LOGGER.debug('updating atuin sync config')

	atuin_config['sync_address'] =  Server.SYNC_ADDRESS
	atuin_config['sync_frequency'] = '0'
	atuin_config['update_check'] = False # we will manage updates ourselves
	atuin_config_file.write_text(tomlkit.dumps(atuin_config))




def get_headers():
	return {'Authorization': f'Bearer {USER_INPUT_INSTALL_TOKEN}'}

def copy_key_to_server(liminal_user_uuid: str):
	LOGGER.info('Copying key')
	key_file = Path('~/.local/share/atuin/key').expanduser()
	files = {
		'file_content': ('key', key_file.open(mode='rb'))
	}
	data = {
		'metadata': json.dumps({'liminal_user_uuid': liminal_user_uuid,})
	}
	response = requests.post(f'{Server.API_ADDRESS}/install/key', data=data, files=files, headers=get_headers())
	Server.assert_response_ok(response)
	PROGRESS_TRACKER['key_copied_to_server'] = True



def _main():
	"""
	"""
	global USER_LIMINAL_UUID
	global USER_INPUT_INSTALL_TOKEN
	LOGGER.debug('Starting ----------')
	print('\nWelcome!')
	print(f'If you haven\'t already, get your install token from {USER_INSTALL_KEY_URL}')
	
	preflight_tests()


	try:
		while not USER_LIMINAL_UUID:
			if not USER_INPUT_INSTALL_TOKEN:
				USER_INPUT_INSTALL_TOKEN = input('\nPlease enter in your Liminal install token: ').strip()
			try:
				USER_LIMINAL_UUID = Server().authenticate_user_provided_key(USER_INPUT_INSTALL_TOKEN)
			except ExpiredToken:
				USER_INPUT_INSTALL_TOKEN = None
				USER_LIMINAL_UUID = None
				LOGGER.error(f'Your install token has expired. Please generate a new one by visiting {USER_INSTALL_KEY_URL}')
	except KeyboardInterrupt:
		LOGGER.debug('user quit')
		sys.exit(2)


	install_atuin()

	ATUIN_REGISTRATION_PASSWORD = str(uuid.uuid4()) # can be random and forgotten since this is for logging in on other machine. if users request in future they want to sync multiple machines, a future update can reset their password
	env_copy = os.environ.copy()
	env_copy['ATUIN_REGISTRATION_PASSWORD'] = ATUIN_REGISTRATION_PASSWORD
	# TODO: handle re-registering. currently will fail the install if user has been registered before
	atuin_username = USER_LIMINAL_UUID.replace('-', '')
	run_command([ATUIN_EXEC_PATH, 'register', '-u', atuin_username, '-e', f'{USER_LIMINAL_UUID}@forward.shellsync.liminalbios.com', '-p', '$ATUIN_REGISTRATION_PASSWORD'], env=env_copy)
	PROGRESS_TRACKER['registered_user_to_atuin'] = True
	copy_key_to_server(USER_LIMINAL_UUID)
	
	test_correctly_setup()

	LAST_SUCCESS_INSTALL_FLAG_PATH.write_text(json.dumps({'date': datetime_utcnow().isoformat(), 'version': LIMINAL_PACKAGE_VERSION}))
	LOGGER.debug('Finished sucesffuly')
	
	confirm_response = requests.post(f'{Server.API_ADDRESS}/install/confirmation', timeout=10, headers=get_headers(), json={
		'liminal_user_uuid': USER_LIMINAL_UUID,
		'python_version': sys.version,
		'os_distribution': get_os_distro_info(),
		'liminal_version': LIMINAL_PACKAGE_VERSION,
	})
	LOGGER.debug(f'{confirm_response.status_code=}')



def cleanup():
	"""Cleanup any mess made by _main(), and make subsequent install attempts possible
	"""
	if config.LIMINAL_INSTALLER_SKIP_CLEANUP == 'yes':
		LOGGER.debug('skipping cleanup')
		return
	if PROGRESS_TRACKER.get('installed_atuin'):
		try:
			uninstall_atuin()
		except Exception:
			LOGGER.debug('issue with cleanup', exc_info=True)
	
	# TODO: if registered_user_to_atuin, unregister them or handle in some way so they can run installer again


def main():
	try:
		_main()
	except Exception:
		report_install_issue()
		cleanup()
		exit(1)
	
	print('\n\nLiminal ShellSync (powered by `atuin`) has been installed!\nPlease logout and login again for ShellSync to start working')


def _report_install_issue():
	debug_info = debug()

	traceback_str = traceback.format_exc()
	payload = {
		'traceback': traceback_str,
		'PROGRESS_TRACKER': PROGRESS_TRACKER,
		'debug_info': debug_info,
		'liminal_user_uuid': USER_LIMINAL_UUID,
		'install_token': USER_INPUT_INSTALL_TOKEN,
		'package_version': LIMINAL_PACKAGE_VERSION,
	}
	LOGGER.exception('Unexpected error during install')
	try:
		print(json.dumps(payload))
	except Exception as e:
		print('Error dumping debug info', e)

	LOGGER.debug(f'sending report issue to server: {payload}')
	# with retries
	requests.post(f'{Server.API_ADDRESS}/install/issue', json=payload)


def report_install_issue():
	try:
		_report_install_issue()
	except Exception:
		LOGGER.exception('Exception when trying to report install issue')
		traceback.print_exc()
	print(f'\n\nThere was an error during installation. Please let us know at {EMAIL_CONTACT} and provide all the output from above')


if __name__ == '__main__':
	main()
