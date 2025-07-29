import collections
import pathlib
import sys
import typing

import nox
import nox.command

import nose_helper.__version__

nox.options.error_on_external_run = True
nox.options.error_on_missing_interpreters = True
nox.options.reuse_existing_virtualenvs = True
nox.options.sessions = []

VENV_PREPARED = ""


class NoxBase:
	"""Base class for NOX checks."""

	def __init__(self, session: nox.Session, project_name=None, changelog_path: typing.Optional[pathlib.Path] = None):
		"""init NOX checks."""
		self._session = session
		self._base_dir = pathlib.Path(__file__).parent.parent.parent.parent.resolve()
		self._project_name = project_name if project_name else self._base_dir.name
		self._changelog_path = changelog_path
		self._silent = False
		self._python_executable: str = sys.executable if isinstance(session.virtualenv, nox.sessions.PassthroughEnv) else "python"

	def _install_requirements(self):
		"""Install requirement files into venv but only if it's not a pass-through venv."""
		global VENV_PREPARED  # pylint: disable=global-statement
		if not isinstance(self._session.virtualenv, nox.sessions.PassthroughEnv) and VENV_PREPARED != self._session.virtualenv.location:
			self._session.install("-U", "pip", silent=self._silent)
			self._session.install("-U", "wheel", silent=self._silent)
			self._session.install("-U", "-r", "requirements.txt", f"nose_helper=={nose_helper.__version__.__version__}", silent=self._silent)

		if not VENV_PREPARED:
			if isinstance(self._session.virtualenv, nox.sessions.PassthroughEnv):
				VENV_PREPARED = sys.executable
			else:
				VENV_PREPARED = self._session.virtualenv.location

	def pylint(self, dir_names: list[str] = None, rcfile: pathlib = None, jobs: int = 4) -> None:
		"""Run pylint.

		:param dir_names: dir names, which should be checked
		:param rcfile: config file for pylint
		:param jobs: count of jobs
		:return:
		"""
		if not dir_names:
			dir_names = [self._project_name, "tests"]

		if not rcfile:
			rcfile = pathlib.Path(__file__).parent / "config/.pylintrc"

		self._install_requirements()
		args = dir_names
		args.append(f"--rcfile={rcfile}")
		args.append(f"--jobs={jobs}")
		self._session.run(self._python_executable, "-m", "pylint", *args, silent=self._silent)

	def coverage(self) -> None:
		"""Run coverage."""
		self._install_requirements()

		run_args = ["--rcfile=.coveragerc"]
		html_args = ["--skip-covered", "--fail-under=100"]
		with self._session.chdir("tests"):
			self._session.run(self._python_executable, "-m", "coverage", "run", *run_args, "run_unittest.py", silent=self._silent)
			try:
				self._session.run(self._python_executable, "-m", "coverage", "html", *html_args, silent=self._silent)
			except nox.command.CommandFailed:
				self._session.warn(f"Coverage result: {(pathlib.Path.cwd() / 'htmlcov/index.html').as_uri()}")
				raise

	def version_check(self, pypi_name: typing.Optional[str] = None, version_file: typing.Optional[str] = None):
		"""Check if version was updated"""
		self._install_requirements()

		pypi_name = pypi_name if pypi_name else self._project_name
		version_file = version_file if version_file else pathlib.Path.cwd() / self._project_name / "__version__.py"

		version_data = {}
		with open(version_file, "r", encoding="utf-8") as file:
			exec(file.read(), version_data)
		branch_version = version_data.get("__version__", "0.0.0")

		self._session.run("python", f"{pathlib.Path(__file__).parent / 'version_check.py'}", "--branch_version", f"{branch_version}", "--pypi_name", f"{pypi_name}", "--changelog_path", f"{self._changelog_path}")


def run_combined_sessions(session: nox.Session, sub_sessions: list[tuple[str, collections.abc.Callable[[], None]]]) -> None:
	"""Run combined nox sessions.

	:param session: nox session that should run the sub sessions
	:param sub_sessions: a list of a pair of name and sub session functions that should be executed
	:raises nox.command.CommandFailed: if one or more sub-sessions fail
	"""
	errors = []
	for name, sub_session in sub_sessions:
		try:
			session.warn(f"Running sub-session {name}")
			sub_session()
		except Exception:  # pylint: disable=broad-except
			errors.append(name)
	if errors:
		session.error(str(errors))
