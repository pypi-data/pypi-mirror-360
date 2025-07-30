import os

from decouple import AutoConfig, Config

from .secrets import CompositeRepository, RepositorySecret

autoconfig = AutoConfig(search_path=os.getcwd())
SECRETS_PATH = autoconfig("SECRETS_PATH", default="/run/secrets/")

repository = CompositeRepository(
    autoconfig.config.repository,
    RepositorySecret(SECRETS_PATH)
)

config: Config = Config(repository)