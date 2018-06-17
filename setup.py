#!/usr/bin/env python

from distutils.core import setup

setup(name="VaLID",
      version="1.0.4",
      description="A language identification system based on prediction by partial matching (PPM) compression",
      author="Paul McNamee",
      author_email="paul.mcnamee@jhuapl.edu",
      url="http://www.hltcoe.jhu.edu",
      maintainer="Tom Lippincott",
      maintainer_email="tom@cs.jhu.edu",
      packages=["valid"],
      package_dir={"valid" : "src/valid"},
      scripts=["scripts/concrete_annotator_server.py", "scripts/concrete_annotator_client.py", "scripts/convert_invalid_to_valid.py", "scripts/valid_example.py"],
      install_requires=["iso639"],
     )
