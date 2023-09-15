from setuptools import setup, find_namespace_packages

setup(
    name='test_clean_Volodymyr_Pryhlo',
    version='0.0.1',
    description="""This code knows how to find different file extensions at different depths of the location 
                   and sort them into the appropriate folders.
                   This is a script that sorts the folder.""",
    url='https://github.com/Famm1/Home_work_module6/blob/main/main.py',
    author='Volodymyr Pruhlo',
    author_email='vova.pruglo22@gmail.com',
    license='MIT',
    packages=find_namespace_packages(),
    install_requires=[],
    entry_points={'console_scripts': ['clean_folder = clean_folder.main:main']}
)
