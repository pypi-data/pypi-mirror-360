# Namespace package declaration for sphinxcontrib
# This file is required for proper namespace package functionality
# according to PEP 420 and setuptools documentation
__path__ = __import__("pkgutil").extend_path(__path__, __name__)
