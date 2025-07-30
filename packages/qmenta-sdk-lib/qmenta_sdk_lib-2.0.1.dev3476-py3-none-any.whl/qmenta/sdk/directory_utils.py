import shutil
import tempfile


class TemporaryDirectory:
    """
    Context manager which creates a temporary directory and removes it automatically.
    """

    def __init__(self):
        self.name = None

    def __enter__(self):
        self.name = tempfile.mkdtemp()
        return self.name

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.name)
