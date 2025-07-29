import sys
import click
import socket
import pathlib
import logging
import importlib

from Git import Git, Repositories, Repository
from . configuration import Configuration



class Application:

	ROOT = pathlib.Path('~/source').expanduser().resolve()

	@classmethod
	def Initialize(self):
		if self.ROOT.exists():
			return

		self.ROOT.mkdir(parents=True, exist_ok=True)

	@classmethod
	def Run(self, args):
		self.Initialize()
		Configuration.Initialize()
		configuration = Configuration()

		application = self(configuration, args)
		status = application.run()

		if status:
			configuration.Write()

	def __init__(self, configuration, args):
		self.configuration = configuration
		self.command = args.command
		self.args = args

	def run(self):
		function = {
			'create': self.Create,
			'add': self.Add,
			'list': self.List,
			'start': self.Start,
			'stop': self.Stop,
			'update': self.Update,
			'process': self.Process,
		}

		fn = function[self.command]
		return fn()

	def hostname(self):
		return socket.gethostname()

	def Create(self):
		hostname = self.hostname()
		repository = self.args.repository

		status = []
		for r in ("webhook", "router", "certbot"):
			url = f'server/{hostname}/{r}'
			done = self.clone(repository, url, errors=False)
			if not done:
				click.echo("Failed " + click.style(f"{url}", fg="red"))
			status.append(done)

		if any(status):
			self.configuration['repository'] = repository
			return True

		return False

	def Add(self):
		repository = self.configuration.get('repository', None)
		path = self.args.path
		if repository is None:
			logging.error("No server deployment found")
			return False

		if (self.ROOT / path).exists():
			logging.error(f'Error: {path} exists')
			return False

		status = self.clone(repository, path, errors=False)
		if status:
			message = "Cloned " + click.style(f"{path}", fg='green')
		else:
			message = "Could not clone " + click.style(f"{path}", fg='red')

		click.echo(message)
		return status

	def Update(self):
		Git.Initialize(self.ROOT)
		for repository in Repositories():
			try:
				repository.pull()
				message = click.style('updated', fg='green')
			except Exception as e:
				message = click.style(f'{e}', fg='red')

			click.echo(f'{repository.path} ' + message)

	def List(self):
		Git.Initialize(self.ROOT)
		for repository in Repositories():
			click.echo(f'{repository.path}')

	def Start(self):
		Git.Initialize(self.ROOT, cached=False)

	def Stop(self):
		Git.Initialize(self.ROOT)

	def clone(self, repository, url, errors=True):
		path = self.ROOT / url
		link = f'{repository}/{url}.git'
		try:
			Repository.Clone(link, path)
			return True
		except Exception:
			if errors:
				raise
			return False

	def handler(self):
		path = self.ROOT / 'webhook'
		if not path.exists():
			logging.error(f"path does not exist: {path}")
			return

		if len(sys.path) == 0 or sys.path[0] != path:
			sys.path.insert(0, path)

		print(sys.path[0])

		try:
			return importlib.import_module('Handler')
		except ModuleNotFoundError as e:
			logging.error(e)
			return

	def Process(self):
		handler = self.handler()
		if handler is None:
			logging.error("Handler could not be imported")
			return

		print(handler)
