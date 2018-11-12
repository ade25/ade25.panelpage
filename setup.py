from setuptools import setup, find_packages
import os

version = '1.0.0'

setup(name='ade25.panelpage',
      version=version,
      description="Manage modular pages with blocks and panels",
      long_description=open("README.txt").read() + "\n" +
      open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='',
      author='Ade25',
      author_email='cb@ade25.de',
      url='http://dist.ade25.de',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ade25'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.beaker',
          'plone.api',
          'plone.app.dexterity [relations]',
          'plone.app.relationfield',
          'plone.namedfile [blobs]',
          'plone.formwidget.querystring',
          #'plone.formwidget.contenttree',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
