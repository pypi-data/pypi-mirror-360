#!/usr/bin/env python
from glob import glob
from pathlib import Path
from setuptools import find_packages, setup
from setuptools.command.build_py import build_py
import subprocess

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()


class CustomBuild(build_py):
    assets = (
        (
            "libjs-bootstrap4",
            "4.3",
            [
                "debconf/static/vendor/bootstrap/scss",
                "debconf/static/vendor/bootstrap/js",
            ],
        ),
        (
            "fonts-fork-awesome",
            "1.1",
            [
                "debconf/static/vendor/fork-awesome/scss",
                "debconf/static/vendor/fork-awesome/fonts",
            ],
        ),
        ("libjs-jquery", "3", ["debconf/static/vendor/jquery/jquery.js"]),
        ("libjs-moment", "2.28", ["debconf/static/vendor/moment/moment-with-locales.js"]),
        ("libjs-moment-timezone", "0.5.31+dfsg1-2", ["debconf/static/vendor/moment-timezone/moment-timezone-with-data.js"]),
        ("node-normalize.css", "8.0.0", ["badges/static/vendor/normalize.css/normalize.css"]),
    )

    def check_assets(self):
        base = Path(__file__).parent
        missing_packages = []
        for package, version, links in self.assets:
            broken_links = [l for l in links if not (base / l).exists()]
            if broken_links:
                try:
                    self.check_deb_package(package, version)
                except RuntimeError as exc:
                    missing_packages.append(str(exc))
        if missing_packages:
            raise RuntimeError("; ".join(missing_packages))

    def check_deb_package(self, package, version):
        try:
            _, instversion = subprocess.check_output(["dpkg-query", "--show", package]).split()
        except subprocess.CalledProcessError:
            raise RuntimeError(f"{package} not installed")
        try:
            subprocess.check_call(["dpkg", "--compare-versions", instversion, "ge", version])
        except subprocess.CalledProcessError:
            raise RuntimeError(f"{package} (>= {version}) required, found {instversion}")

    def run(self):
        self.check_assets()
        super().run()


def compile_translations():
    try:
        subprocess.check_call(['./manage.py', 'compilemessages'])
    except subprocess.CalledProcessError:
        print("WARNING: cannot compile translations.")
        pass
    return glob('*/locale/*/LC_MESSAGES/django.mo')


setup(
    name='wafer-debconf',
    version='0.16.11',
    description='Wafer extensions used by DebConf',
    author='DebConf Team',
    author_email='debconf-team@lists.debian.org',
    url='https://salsa.debian.org/debconf-team/public/websites/wafer-debconf',
    packages=find_packages(exclude=['tests', 'tests.*']),
    cmdclass={
        "build_py": CustomBuild,
    },
    include_package_data=True,
    package_data={
        "badges": ["static/*", "static/vendor/*/*"],
        "debconf": ["static/vendor/*", "static/vendor/*/*", "static/vendor/*/*/*"],
        "register": ["static/register/*", "static/vendor/*", "static/vendor/*/*", "static/vendor/*/*/*"],
    },
    data_files=compile_translations(),
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        "mdx_linkify",
        "wafer>=0.16,<0.17",
        "mdx_staticfiles",
        "Django>=3,<5",
        "django_compressor",
        "django_countries",
        "django_extensions",
        "django_libsass",
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Communications :: Conferencing',
    ],
)
