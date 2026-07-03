import os
import sys

# Make the top-level bot modules (config, content_builder, printful_client, ...)
# importable regardless of the directory pytest is invoked from.
sys.path.insert(0, os.path.dirname(__file__))
