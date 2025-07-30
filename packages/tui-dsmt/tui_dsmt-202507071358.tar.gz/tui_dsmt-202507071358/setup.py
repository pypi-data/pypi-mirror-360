requirements = [
    'jupyter',
    'ipywidgets',
    'checkmarkandcross',
    'fa2_modified==0.3.10',
    'ipyparallel==9.0.1',
    'ipython==9.2.0',  # separate install... otherwise, IPython.utils.coloransi cannot be found
    'matplotlib==3.10.3',
    'mlxtend==0.23.4',
    'mpi4py==4.0.3',  # mpi4py is installed via conda (see Dockerfile)
    'networkx==3.4.2',
    'numpy==2.2.6',
    'plotly==6.1.0',
    'pandas==2.2.3',
    'pyarrow==20.0.0',
    'pyfpgrowth==1.0',
    'pyspark==3.5.5',
    'scikit-learn==1.6.1',
    # 'scikit-learn-extra==0.3.0',
]

if __name__ == '__main__':
    version = '202507071358'

    from setuptools import setup, find_packages
    setup(
        name='tui_dsmt',
        version=version,
        author='Eric Tröbs',
        author_email='eric.troebs@tu-ilmenau.de',
        description='everything you need for our jupyter notebooks',
        long_description='everything you need for our jupyter notebooks',
        long_description_content_type='text/markdown',
        url='https://dbgit.prakinf.tu-ilmenau.de/lectures/data-science-methoden-und-techniken',
        project_urls={},
        classifiers=[
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
        ],
        package_dir={'': 'src'},
        packages=find_packages(where='src'),
        python_requires='>=3.10',
        install_requires=requirements,
        package_data={
            'tui_dsmt': [
                'jpanim/resources/*',
                'clustering/resources/*',
                'fpm/resources/*',
                'graph/resources/*',
                'parallel/resources/*',
            ]
        },
        include_package_data=True
    )
