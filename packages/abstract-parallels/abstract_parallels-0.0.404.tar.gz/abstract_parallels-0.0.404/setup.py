from time import time
import setuptools
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setuptools.setup(
    name='abstract_parallels',
    version='0.0.404',
    author='putkoff',
    author_email='partners@abstractendeavors.com',
    description="A Python package for managing clipboard, window info, services, and APIs with GUI interfaces",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/abstractendeavors/abstract_parallels',  # Update with actual repo if available
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    package_data={
        'abstract_parallels': [
            '*.sh',
            'apis/*.sh',
            'clipit/*.sh',
            'services_mgr/*.sh',
            'window_mgr/*.sh',
        ]
    },
        include_package_data=True,
    install_requires=[
        'flask',
        'paramiko',
        'PyQt5',
        # 'abstract_utilities',  # Uncomment if external dependency
    ],


    python_requires=">=3.6",
    setup_requires=['wheel'],

)
