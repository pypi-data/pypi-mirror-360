



import datetime
import getpass
import os
from pathlib import Path
import platform
import pwd
import socket
import subprocess
import sys

import psutil

from liminal.standalone_install_wrapper import LIMINAL_DIR

LAST_SUCCESS_INSTALL_FLAG_PATH = LIMINAL_DIR / 'install-successful'

ATUIN_EXEC_PATH = Path.home() / '.atuin/bin/atuin' # since PATH for env/shell wont be updated


def datetime_utcnow() -> datetime.datetime:
	return datetime.datetime.now(datetime.timezone.utc)





def _run_command(command_parts, timeout=3):
	"""
	Helper function to run a shell command and return its output.
	Returns (stdout, stderr, return_code)
	"""
	try:
		process = subprocess.run(
			command_parts,
			capture_output=True,
			text=True,
			timeout=timeout,
			check=False  # Don't raise exception for non-zero exit codes
		)
		return process.stdout.strip(), process.stderr.strip(), process.returncode
	except FileNotFoundError:
		return f"Error: Command '{command_parts[0]}' not found.", "", -1
	except subprocess.TimeoutExpired:
		return f"Error: Command '{' '.join(command_parts)}' timed out after {timeout}s.", "", -2
	except Exception as e:
		return f"Error running '{' '.join(command_parts)}': {str(e)}", "", -3


def get_os_distro_info() -> dict[str, str]:
	os_distro = {}
	# Try /etc/os-release (standard for modern distros)
	try:
		with open("/etc/os-release", "r") as f:
			for line in f:
				line = line.strip()
				if not line or line.startswith("#") or "=" not in line:
					continue
				key, value = line.split("=", 1)
				# Remove quotes from value if present
				value = value.strip('"')
				os_distro[f"os_release_{key.lower()}"] = value
	except FileNotFoundError:
		os_distro["os_release_file"] = "Not found (/etc/os-release)"
	except Exception as e:
		os_distro["os_release_file_error"] = str(e)

	# Try lsb_release command (common but not always present)
	if not os_distro.get("os_release_pretty_name"): # If /etc/os-release didn't give a good name
		lsb_out, lsb_err, lsb_ret = _run_command(["lsb_release", "-a"])
		if lsb_ret == 0 and lsb_out:
			for line in lsb_out.splitlines():
				if ":" in line:
					key, value = line.split(":", 1)
					os_distro[f"lsb_{key.strip().lower().replace(' ', '_')}"] = value.strip()
		elif lsb_ret == -1: # Command not found
			os_distro["lsb_release_command"] = "Not found"
		elif lsb_err:
			os_distro["lsb_release_error"] = lsb_err

	# Fallback: /etc/issue (less structured)
	if not os_distro.get("os_release_pretty_name") and not os_distro.get("lsb_distributor_id"):
		try:
			with open("/etc/issue", "r") as f:
				os_distro["etc_issue"] = f.read().strip()
		except FileNotFoundError:
			os_distro["etc_issue_file"] = "Not found (/etc/issue)"
		except Exception as e:
			os_distro["etc_issue_file_error"] = str(e)
	return os_distro

def get_linux_debug_info():
	"""
	Gathers various pieces of debug information from a Linux/Unix system.
	Returns a dictionary of debug information.
	"""
	info = {}

	# --- Basic System Information ---
	info["python_version"] = sys.version
	info["python_executable"] = sys.executable
	info["platform_system"] = platform.system()
	info["platform_release"] = platform.release()
	info["platform_version"] = platform.version()
	info["platform_machine"] = platform.machine()
	info["platform_node"] = platform.node() # hostname
	info["platform_uname"] = str(platform.uname())

	info["os_distribution"] = get_os_distro_info()

	# --- Kernel Information ---
	kernel_info = {}
	uname_r, _, ret = _run_command(["uname", "-r"]) # Kernel release
	if ret == 0: kernel_info["kernel_release"] = uname_r
	uname_v, _, ret = _run_command(["uname", "-v"]) # Kernel version
	if ret == 0: kernel_info["kernel_version"] = uname_v
	uname_a, _, ret = _run_command(["uname", "-a"]) # All kernel info
	if ret == 0: kernel_info["kernel_all"] = uname_a
	info["kernel_info"] = kernel_info
	
	   # --- Network Information ---
	network_info = {}
	try:
		network_info["hostname"] = socket.gethostname()
		network_info["fqdn"] = socket.getfqdn()
		# Note: socket.gethostbyname can be slow or fail if DNS isn't perfect
		try:
			network_info["ip_address_via_socket"] = socket.gethostbyname(network_info["hostname"])
		except socket.gaierror:
			network_info["ip_address_via_socket"] = "Could not resolve hostname to IP"
	except Exception as e:
		network_info["socket_error"] = str(e)

	ip_addr_out, ip_addr_err, ip_addr_ret = _run_command(["ip", "addr"])
	if ip_addr_ret == 0 and ip_addr_out:
		network_info["ip_addr_show"] = ip_addr_out
	else: # Fallback to ifconfig if 'ip' command failed or not found
		ifconfig_out, ifconfig_err, ifconfig_ret = _run_command(["ifconfig"])
		if ifconfig_ret == 0 and ifconfig_out:
			network_info["ifconfig"] = ifconfig_out
		else:
			if ip_addr_ret == -1 : network_info["ip_command"] = "Not found"
			elif ip_addr_err: network_info["ip_command_error"] = ip_addr_err
			if ifconfig_ret == -1: network_info["ifconfig_command"] = "Not found"
			elif ifconfig_err: network_info["ifconfig_command_error"] = ifconfig_err
				
	# DNS servers
	try:
		with open("/etc/resolv.conf", "r") as f:
			network_info["dns_servers_resolv_conf"] = [
				line.split()[1] for line in f if line.strip().startswith("nameserver")
			]
	except FileNotFoundError:
		network_info["resolv_conf"] = "Not found"
	except Exception as e:
		network_info["resolv_conf_error"] = str(e)
	info["network_info"] = network_info

	# --- User and Environment ---
	user_env_info = {}
	user_env_info["current_user"] = os.getenv("USER", "N/A")
	user_env_info["effective_uid"] = os.geteuid()
	user_env_info["effective_gid"] = os.getegid()
	
	id_out, id_err, id_ret = _run_command(["id"])
	if id_ret == 0: user_env_info["id_command"] = id_out
	else: user_env_info["id_command_error"] = id_err if id_err else "Command failed or not found"

	user_env_info["path_env_var"] = os.getenv("PATH", "N/A")
	user_env_info["home_env_var"] = os.getenv("HOME", "N/A")
	user_env_info["lang_env_var"] = os.getenv("LANG", "N/A")
	user_env_info["locale_output"] = _run_command(["locale"])[0] # Get first element (stdout)
	info["user_environment"] = user_env_info


	return info





class Shell:


	def __init__(self):
		self.exec_path = self.get_default_shell_path()
		self.name = self.exec_path.name
		self.config_file = Path.home() / '.bashrc' if self.is_bash() else Path.home() / '.zshrc'

		# {
		# 	'bash': ['.bashrc', '.bash_profile', '.bash_login', '.profile'],
		# 	'zsh': ['.zshrc', '.zshenv', '.zprofile', '.zlogin']
		# }


	def dict(self):
		return {
			'name': self.exec_path.name,
			'exec_path': self.exec_path.as_posix(),
			'version': subprocess.run([self.exec_path, '--version'], check=False, capture_output=True, text=True, timeout=1).stdout,
			'envvar_SHLVL': os.environ.get('SHLVL'),
			'envvar_TERM': os.environ.get('TERM'),
			'envvar_PS1': os.environ.get('PS1'), # certain PS1 might not match for our command testing (hack.run_logingcommand pexpect.)
		}

	def is_supported(self):
		return self.exec_path.name in ['bash', 'zsh']
	
	def is_bash(self):
		return self.exec_path.name == 'bash'

	def get_default_shell_path(self) -> Path:
		"""Gets the default shell for the current user."""
		user_id = os.getuid()
		user_info = pwd.getpwuid(user_id)
		return Path(user_info.pw_shell)
		
	def this_process_shell_path(self) -> Path:
		parent_pid = os.getppid()
		parent_process = psutil.Process(parent_pid)
		# .exe() gives the full path, .name() just the command name (e.g., 'bash')
		# We prefer .exe() for uniqueness
		shell_exe = parent_process.exe()
		return Path(shell_exe)



def path_metadata(given_path: Path, depth=1) -> dict:
	path = given_path.expanduser()
	metadata = {
		'given_path': given_path.as_posix(),
		'resolved_path': path.as_posix(),
		'exists': path.exists(),
	}

	if path.exists():
		metadata = metadata | {
			'date_created': path.stat().st_ctime,
			'date_modified': path.stat().st_mtime,
			'owner': path.owner(),
			'size': path.stat().st_size,
		}
	if path.is_dir():
		metadata['child_count'] = len(list(path.glob('*')))
		if depth > 0:
			metadata['children'] = []
			for child in path.iterdir():
				metadata['children'].append(path_metadata(child, depth=depth-1))

	return metadata


def check_atuin_install() -> dict:
	atuin_is_installed_in_path = False
	try:
		subprocess.run(['atuin', '--help'], check=True, capture_output=True)
		atuin_is_installed_in_path = True
	except (subprocess.CalledProcessError, FileNotFoundError):
		pass
	
	atuin_is_installed_in_home = ATUIN_EXEC_PATH.exists()

	atuin_doctor = None
	if atuin_is_installed_in_home:
		task = subprocess.run([ATUIN_EXEC_PATH, 'doctor'], capture_output=True, text=True, check=False)
		atuin_doctor = task.stdout
	
	return {
		'is_installed_in_path': atuin_is_installed_in_path,
		'is_installed_in_home': atuin_is_installed_in_home,
		'atuin_doctor_output': atuin_doctor,
		'paths': [
			path_metadata(Path('~/.local/share/atuin/'), ),
			path_metadata(Path('~/.config/atuin/'), ),
			path_metadata(Path('~/.atuin/'), ),
		],
	}


def debug():
	"""
	which shells are available. /etc/shells

	if all expected atuin files/dirs exist, and their mod times

	"""
	# python -m site

	last_install = None
	if LAST_SUCCESS_INSTALL_FLAG_PATH.exists():
		last_install = LAST_SUCCESS_INSTALL_FLAG_PATH.read_text()


	return {
		'datetime': datetime_utcnow().isoformat(),
		'argv': sys.argv,
		'user': {
			'username': getpass.getuser(), 
			'uid': os.getuid(),
			'gid': os.getgid(),
		},
		'shell': Shell().dict(),
		'info': get_linux_debug_info(),
		'python': {
			'pip_freeze': subprocess.run([sys.executable, '-m', 'pip', 'freeze'], capture_output=True, text=True, check=False).stdout,
			'path': sys.path
		},
		'last_sucessful_install': last_install,
		'atuin': check_atuin_install(),
	}
