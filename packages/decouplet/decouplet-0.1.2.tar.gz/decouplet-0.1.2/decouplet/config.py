from decouple import AutoConfig, Config
from .secrets import RepositorySecret, CompositeRepository

autoconfig = AutoConfig()
SECRETS_PATH = autoconfig("SECRETS_PATH", default="/run/secrets/")

repository = CompositeRepository(
    autoconfig.config.repository,
    RepositorySecret(SECRETS_PATH)
)

config: Config = Config(repository)