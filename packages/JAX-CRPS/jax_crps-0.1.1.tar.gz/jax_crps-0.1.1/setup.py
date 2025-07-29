from setuptools import setup, find_packages

setup(
    name="JAX_CRPS",
    version="0.1.1",
    description="A simple package implementing the Continuous Ranked Probability Score (CRPS) using JAX",
    author="James Woodfield",
    author_email="notmyemail@dontwebscrapeme.com",
    packages=find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=["jax>=0.4.0"],
)