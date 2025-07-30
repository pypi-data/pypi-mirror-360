from tenyks_sdk.sdk.client import Client


class Workspace:
    def __init__(
        self,
        client: Client,
        workspace_name: str,
        public: bool,
        status: str,
    ) -> "Workspace":
        self.client = client
        self.name = workspace_name
        self.public = public
        self.status = status

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={repr(self.name)}, "
            f"public={repr(self.public)}, "
            f"status={repr(self.status)})"
        )
