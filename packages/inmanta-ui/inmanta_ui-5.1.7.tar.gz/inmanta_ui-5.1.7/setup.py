from setuptools import setup, find_packages

requires = [
    "inmanta-core>=11.1.0.dev",
    "tornado~=6.0",
]

namespace_packages = ["inmanta_ext.ui"]

setup(
    version="5.1.7",
    python_requires=">=3.11",  # also update classifiers
    # Meta data
    name="inmanta-ui",
    description="Slice serving the inmanta UI",
    author="Inmanta",
    author_email="code@inmanta.com",
    url="https://github.com/inmanta/inmanta-ui",
    license="ASL 2.0",
    project_urls={
        "Bug Tracker": "https://github.com/inmanta/inmanta-ui/issues",
    },
    # Packaging
    package_dir={"": "src"},
    packages= namespace_packages + find_packages("src"),
    package_data={"": ["misc/*", "docs/*"]},
    include_package_data=True,
    install_requires=requires,
    extras_require={
        "dev": [
            "bumpversion",
            "inmanta-dev-dependencies[pytest,async,extension]",
        ],
    },
    entry_points={
    },
)
