"""
this seems to be the only way to run a command from python and have atuin record it

subprocess.run(['bash', '-ic', 'mycommand; exit']) doesnt work
	# resp = subprocess.run(['bash', '-ic', f'logger "liminal installed {datetime_utcnow()} {uuid4()}"'])
	resp = subprocess.run(['bash', '-ic', f'eval "$(atuin init bash)"; echo pleaseeee; true; exit 0'], cwd=Path(__file__).parent.parent, env=None)
"""
import sys
import pexpect

from liminal.standalone_install_wrapper import LOGGER

def run_login_command(shell_exec_path: str, cmd: str):
	shell_command = f"{shell_exec_path} -l"
	LOGGER.info(f"{shell_exec_path} -l '{cmd}'")
	child = pexpect.spawn(shell_command, encoding='utf-8', timeout=10)
	# child.logfile = sys.stdout
	prompt = r"[$#] " # Common prompt pattern for bash/sh

	try:
		child.expect(prompt, timeout=5)
		child.sendline(cmd)
		child.expect(prompt, timeout=5)
		raw_cmd_output = child.before
		return raw_cmd_output
	finally:
		child.terminate()
		child.close()  

if __name__ == '__main__':
	import uuid 
	# run_in_pty_shell('/bin/bash', f'logger "ok {uuid.uuid4()}"')
	run_login_command('/bin/bash', f'logger "ok {uuid.uuid4()}"')
