from setuptools import setup, find_packages

setup(
    name="rlnav",
    version="1.4.15",
    description="Reinforcement Learning Navigation Environments for Gymnasium",
    author="Hedwin Bonnavaud",
    author_email="hbonnavaud@gmail.com",
    packages=find_packages(),
    install_requires=[
        "gym>=0.26",
        "gymnasium>=1.1",
        "pygame",
        "mujoco-py",
        "numpy",
        "opencv-python",
        "matplotlib",
        "scipy",
        "scikit-image",
        "imageio",
        "networkx"
    ],
    include_package_data=True,
    python_requires=">=3.8",
)
