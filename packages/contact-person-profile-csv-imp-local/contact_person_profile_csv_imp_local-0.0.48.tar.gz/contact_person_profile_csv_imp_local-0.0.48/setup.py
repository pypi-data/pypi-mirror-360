import setuptools

PACKAGE_NAME = 'contact-person-profile-csv-imp-local'
package_dir = PACKAGE_NAME.replace("-", "_")

setuptools.setup(
    name=PACKAGE_NAME,
    version='0.0.48',  # https://pypi.org/project/contact-person-profile-csv-imp-local/

    author="Circles",
    author_email="info@circles.ai",
    description="PyPI Package for Circles CSVToContactPersonProfile-local Local/Remote Python",
    long_description="This is a package for sharing common XXX function used in different repositories",
    long_description_content_type="text/markdown",
    packages=[package_dir],
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    url=f"https://github.com/circles-zone/{PACKAGE_NAME}-python-package",
    classifiers=[
        "Programming Language :: Python :: 3",
        # "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'contact-local>=0.0.48',
        'logger-local>=0.0.135',
        'database-mysql-local>=0.1.1',
        'user-context-remote>=0.0.77',
        'contact-email-address-local>=0.0.8',
        'contact-group-local>=0.0.68',
        'contact-location-local>=0.0.14',
        'contact-notes-local>=0.0.33',
        'contact-persons-local>=0.0.8',
        'contact-phone-local>=0.0.12',
        'contact-profile-local>=0.0.7',
        'contact-user-external-local>=0.0.13',
        'importer-local>=0.0.54',
        'internet-domain-local>=0.0.8',
        'location-local>=0.0.104',
        'organization-profile-local>=0.0.4',
        'organizations-local>=0.0.14',
        'python-sdk-remote>=0.0.93',
        'url-remote>=0.0.91',
        'user-external-local>=0.0.114',
        'chardet>=5.2.0'
    ]
)
