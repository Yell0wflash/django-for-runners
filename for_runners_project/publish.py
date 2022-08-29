from pathlib import Path

from poetry_publish.publish import poetry_publish
from poetry_publish.utils.subprocess_utils import verbose_check_call

import for_runners


PACKAGE_ROOT = Path(for_runners.__file__).parent.parent


def publish():
    """
    Publish to PyPi
    Call this via:
        $ poetry run publish
    """
    verbose_check_call('make', 'pytest')  # don't publish if tests fail

    poetry_publish(
        package_root=PACKAGE_ROOT,
        version=for_runners.__version__,
    )
