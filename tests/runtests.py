import os
import sys
import pytest


if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.abspath('.')))
    pytest.main("-q -s --tb=native -n4")