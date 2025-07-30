from glob import glob
import os
import sys
from setuptools import setup

if sys.version_info[:2] < (3, 7):
    error = (
        "Graphdict 3.4+ requires Python 3.7 or later (%d.%d detected). \n"
    )
    sys.stderr.write(error + "\n")
    sys.exit(1)


name = "graphdict"
description = "Python package for creating and manipulating graphs and networks"
authors = {
    "Hagberg": ("John Smith", "johnsmithdev92@gmail.com"),
}
maintainer = "Graphdict Developers"
maintainer_email = "graphdict-discuss@googlegroups.com"
url = "https://networkx.org/"
project_urls = {
    "Bug Tracker": "https://github.com/taylortech75/graphdict/issues",
    "Documentation": "https://networkx.org/documentation/stable/",
    "Source Code": "https://github.com/taylortech75/graphdict",
}
platforms = ["Linux", "Mac OSX", "Windows", "Unix"]
keywords = [
    "Networks",
    "Graph Theory",
    "Mathematics",
    "network",
    "graph",
    "discrete mathematics",
    "math",
]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: BSD License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3 :: Only",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Scientific/Engineering :: Bio-Informatics",
    "Topic :: Scientific/Engineering :: Information Analysis",
    "Topic :: Scientific/Engineering :: Mathematics",
    "Topic :: Scientific/Engineering :: Physics",
]

with open("graphdict/__init__.py") as fid:
    for line in fid:
        if line.startswith("__version__"):
            version = line.strip().split()[-1][1:-1]
            break

packages = [
    "graphdict",
    "graphdict.algorithms",
    "graphdict.algorithms.assortativity",
    "graphdict.algorithms.bipartite",
    "graphdict.algorithms.node_classification",
    "graphdict.algorithms.centrality",
    "graphdict.algorithms.community",
    "graphdict.algorithms.components",
    "graphdict.algorithms.connectivity",
    "graphdict.algorithms.coloring",
    "graphdict.algorithms.flow",
    "graphdict.algorithms.minors",
    "graphdict.algorithms.traversal",
    "graphdict.algorithms.isomorphism",
    "graphdict.algorithms.shortest_paths",
    "graphdict.algorithms.link_analysis",
    "graphdict.algorithms.operators",
    "graphdict.algorithms.approximation",
    "graphdict.algorithms.tree",
    "graphdict.classes",
    "graphdict.generators",
    "graphdict.drawing",
    "graphdict.linalg",
    "graphdict.readwrite",
    "graphdict.readwrite.json_graph",
    "graphdict.tests",
    "graphdict.testing",
    "graphdict.utils",
]

docdirbase = "share/doc/graphdict-%s" % version
# add basic documentation
data = [(docdirbase, glob("*.txt"))]
# add examples
for d in [
    ".",
    "advanced",
    "algorithms",
    "basic",
    "3d_drawing",
    "drawing",
    "graph",
    "javascript",
    "jit",
    "pygraphviz",
    "subclass",
]:
    dd = os.path.join(docdirbase, "examples", d)
    pp = os.path.join("examples", d)
    data.append((dd, glob(os.path.join(pp, "*.txt"))))
    data.append((dd, glob(os.path.join(pp, "*.py"))))
    data.append((dd, glob(os.path.join(pp, "*.bz2"))))
    data.append((dd, glob(os.path.join(pp, "*.gz"))))
    data.append((dd, glob(os.path.join(pp, "*.mbox"))))
    data.append((dd, glob(os.path.join(pp, "*.edgelist"))))
# add js force examples
dd = os.path.join(docdirbase, "examples", "javascript/force")
pp = os.path.join("examples", "javascript/force")
data.append((dd, glob(os.path.join(pp, "*"))))

# add the tests
package_data = {
    "graphdict": ["tests/*.py"],
    "graphdict.algorithms": ["tests/*.py"],
    "graphdict.algorithms.assortativity": ["tests/*.py"],
    "graphdict.algorithms.bipartite": ["tests/*.py"],
    "graphdict.algorithms.node_classification": ["tests/*.py"],
    "graphdict.algorithms.centrality": ["tests/*.py"],
    "graphdict.algorithms.community": ["tests/*.py"],
    "graphdict.algorithms.components": ["tests/*.py"],
    "graphdict.algorithms.connectivity": ["tests/*.py"],
    "graphdict.algorithms.coloring": ["tests/*.py"],
    "graphdict.algorithms.minors": ["tests/*.py"],
    "graphdict.algorithms.flow": ["tests/*.py", "tests/*.bz2"],
    "graphdict.algorithms.isomorphism": ["tests/*.py", "tests/*.*99"],
    "graphdict.algorithms.link_analysis": ["tests/*.py"],
    "graphdict.algorithms.approximation": ["tests/*.py"],
    "graphdict.algorithms.operators": ["tests/*.py"],
    "graphdict.algorithms.shortest_paths": ["tests/*.py"],
    "graphdict.algorithms.traversal": ["tests/*.py"],
    "graphdict.algorithms.tree": ["tests/*.py"],
    "graphdict.classes": ["tests/*.py"],
    "graphdict.generators": ["tests/*.py", "atlas.dat.gz"],
    "graphdict.drawing": ["tests/*.py"],
    "graphdict.linalg": ["tests/*.py"],
    "graphdict.readwrite": ["tests/*.py"],
    "graphdict.readwrite.json_graph": ["tests/*.py"],
    "graphdict.testing": ["tests/*.py"],
    "graphdict.utils": ["tests/*.py"],
}


def parse_requirements_file(filename):
    with open(filename) as fid:
        requires = [l.strip() for l in fid.readlines() if not l.startswith("#")]

    return requires


install_requires = []
extras_require = {
    dep: parse_requirements_file("requirements/" + dep + ".txt")
    for dep in ["default", "developer", "doc", "extra", "test"]
}

with open("README.rst", "r") as fh:
    long_description = fh.read()

if __name__ == "__main__":

    setup(
        name=name,
        version=version,
        maintainer=maintainer,
        maintainer_email=maintainer_email,
        author=authors["Hagberg"][0],
        author_email=authors["Hagberg"][1],
        description=description,
        keywords=keywords,
        long_description=long_description,
        platforms=platforms,
        url=url,
        project_urls=project_urls,
        classifiers=classifiers,
        packages=packages,
        data_files=data,
        package_data=package_data,
        install_requires=install_requires,
        extras_require=extras_require,
        python_requires=">=3.7",
        zip_safe=False,
    )
