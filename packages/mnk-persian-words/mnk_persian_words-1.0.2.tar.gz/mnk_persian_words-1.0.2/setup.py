from setuptools import find_packages, setup

setup(
    name='mnk_persian_words',
    packages=find_packages(include=['mnk_persian_words']),
    version='1.0.2',
    description='Creates REALLY random Persian words',
    author='Masoud Najafzadeh Kalat',
    license='MIT',
    long_description=open('README.md',encoding="utf-8").read(),
    long_description_content_type="text/markdown",

    author_email="masoudnk2@gmail.com",
    url="https://github.com/masoudnk/PersianWordsLib",
    include_package_data=True,
    package_data={
        # "mnk_persian_words": ["data/*.zip", "data/*.gz"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: Persian",
    ],
    python_requires='>=3.7',
)
