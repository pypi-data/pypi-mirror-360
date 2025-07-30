import json
import typer


app = typer.Typer()

@app.command()
def info():
	from .env import debug

	print('Liminal\'s ShellSync is powered by atuin: https://atuin.sh/')
	print(json.dumps(debug(), indent='\t'))


# @app.command()
# def prompt_upgrade():
# 	input('Would you like to upgrade from Liminal v{} to v{}?')


@app.command()
def install():
	from liminal import installer
	installer.main()


if __name__ == '__main__':
	app()
