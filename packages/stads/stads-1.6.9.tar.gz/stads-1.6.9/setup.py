from setuptools import setup, find_packages

modules = [
    "config",
    "evaluation",
    "image_processing",
    "interpolator",
    "microscope",
    "random_sampler",
    "read_images",
    "stads",
    "stads_helpers",
    "stratified_sampler",
    "stratified_sampler_helpers",
    "utility_functions",
]

setup(
    name="stads",
    version='1.6.9',
    author='Akarsh Bharadwaj',
    author_email="akarsh_sudheendra.bharadwaj@dfki.de",
    description='a spatiotemporal statistics-based adaptive sampling algorithm',
    package_dir={"": "src"},
    py_modules=modules,
    packages=find_packages(where="src"),

    url="https://github.com/bharadwajakarsh/stads_adaptive_sampler",
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    install_requires=["numpy","scikit-image","matplotlib","scipy","joblib",
                      "numba", "opencv-python", "ipywidgets","ipython", "tqdm", "requests"],
    python_requires=">=3.8"
)
