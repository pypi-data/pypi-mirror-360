import sys
from distutils.core import setup

if not any(cmd in sys.argv for cmd in ["sdist", "egg_info"]):
    raise Exception(
        """
        Installation terminated!
        This is a stub package intended to mitigate the risks of dependency confusion.
        It holds a once-popular package name removed by its author (or for other reasons, such as security).
        This is package not intended to be installed and highlight problems in your setup.
        
        Read more: https://protsenko.dev/dependency-confusion
        """
    )

setup()
