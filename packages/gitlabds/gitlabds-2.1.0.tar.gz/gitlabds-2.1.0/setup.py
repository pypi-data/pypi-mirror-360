import setuptools, os
from pathlib import Path

if os.environ.get('CI_COMMIT_TAG'):
    version = os.environ['CI_COMMIT_TAG']
elif os.environ.get('CI_JOB_ID'):
    version = os.environ['CI_JOB_ID']
else:
    version = "0.0.0-dev"

requires = ["pandas>=2.1.4", "numpy>=1.26.4", "scipy>=1.13.1", "scikit-learn>=1.5.1", "imbalanced-learn>=0.12.3", "seaborn>=0.13.2", "shap>=0.46.0", "tqdm>=4.66.1"]

# read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name='gitlabds',
    version=version,
    description='Gitlab Data Science and Modeling Tools',
    long_description = long_description,
    long_description_content_type ='text/markdown',
    author='Kevin Dietz',
    author_email='kdietz@gitlab.com',
    packages=setuptools.find_packages(),
    url='https://gitlab.com/gitlab-data/gitlabds',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],
    python_requires= '>=3.10',
    install_requires=requires,
)  

