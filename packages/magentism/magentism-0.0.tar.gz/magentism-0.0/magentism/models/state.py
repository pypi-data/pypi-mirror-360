import os
import enum
import uuid

from config import PROJECT_PATH
from ._base import Base, Unique


class RepositoryType(enum.Enum):
    PYTHON = "python"
    TYPESCRIPT = "typescript"

class Repository(Base):
    name: str
    type: RepositoryType
    description: str
    port: int
    external_identifier: int

    __indexes__ = [Unique("external_identifier")]

    @property
    def path(self):
        return os.path.join(PROJECT_PATH, "repositories", self.name)

    # server things

    def server_run(self):
        pass

    def server_status(self, lines: int):
        pass

    # run things

    def run_command(self, command: str):
        """Run command in the container, starting in the repository
        Returns a `CommandResult`, with:
        stderr, stdout, time, exit code, command
        """

    def run_sql(self, code: str):
        path = f"{uuid.uuid4()}.sql"
        self.file_create(path)
        return self.run_command(f"postgresql -f {path}")

    def run_python(self, code: str):
        # first, call agent to check which additional packages are required to run this code
        path = f"{uuid.uuid4()}.py"
        self.file_create(path)
        return self.run_command(f"python3 {path}")

    # Files manipulation

    def file_read(self, path: str, limit: int=2**14) -> str | None:
        fullpath = os.path.join(self.path, path)
        if not os.path.isfile(fullpath):
            return None
        return open(fullpath, "r").read(limit)

    def file_create(self, path: str, content: str|None = None) -> bool:
        fullpath = os.path.join(self.path, path)
        open(fullpath, "w").write(content or "")

    def file_list(self) -> list[str]:
        pass

    def file_edit(self, path: str, selector: str, action, content: str):
        pass

    def file_remove(self, path: str):
        pass

    def file_rename(self, from_path: str, to_path: str):
        pass

    def file_copy(self, from_path: str, to_path: str):
        pass

    # Git

    def git_branch_create(self, issue_id: int) -> str:
        pass

    def git_branch_select(self, issue_id: int) -> str:
        pass

    def git_branch_commit(self, message: str, files: list[str]):
        pass

    def git_branch_status(self):
        pass

    def git_branch_merge(self) -> id:
        pass

    def git_branch_list(self) -> list[str]:
        pass

    def git_ignore(self, patterns: list[str]) -> list[str]:
        pass


class State(Base):

    current_repository: Repository|None = None

    # about repositories

    def repositories_synchronize(self):
        pass

    def repository_select(self, name: str) -> bool:
        repository = Repository.load(name=name)
        if repository is None:
            return False
        self.current_repository = repository
        self.save()
        return True

    def repository_create(self, type: RepositoryType, name: str, description: str) -> bool:
        repository = Repository(name=name,
                                type=type,
                                description=description,
                                port=0,
                                external_identifier=0)


current_state = State.load(last_created=True) or State()

current_state.repository_create(RepositoryType.PYTHON, "backend", "python backend for the app")
print(Repository.load(last_created=True))
