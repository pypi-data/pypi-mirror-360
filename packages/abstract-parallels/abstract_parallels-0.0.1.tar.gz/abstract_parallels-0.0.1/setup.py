import setuptools
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='abstract_parallels',
    version='0.0.1',
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
    install_requires=[
        'flask',
        'paramiko',
        'PyQt5',
        # 'abstract_utilities',  # Uncomment if external dependency
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
    python_requires=">=3.6",
    setup_requires=['wheel'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'abstract-parallels-dashboard=abstract_parallels.__main__:run_dashboard',
            'abstract-parallels-setup=abstract_parallels.__main__:run_setup',
            'abstract-parallels-service-manager=abstract_parallels.__main__:run_service_manager',
            'abstract-parallels-clipit-gui=abstract_parallels.__main__:run_clipit_gui',
            'abstract-parallels-api-gui=abstract_parallels.__main__:run_api_gui',
            'abstract-parallels-window-mgr=abstract_parallels.__main__:run_window_mgr',
        ]
    },
)
