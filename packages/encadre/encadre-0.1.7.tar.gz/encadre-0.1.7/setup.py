from setuptools import setup

console_scripts = """
encadre-test-app-serve = encadre_test_app:serve
encadre-test-app-dump-routes = encadre_test_app:dump_routes
"""

setup(name='encadre',
      version='0.1.7',
      description="Encadre framework",
      author="Jean Schurger",
      author_email='jean@schurger.org',
      packages=['encadre', 'encadre_flask'],
      install_requires=['Flask', 'fastjsonschema', 'flask-cors',
                        'decorator', 'nose', 'coverage', 'flask_jwt_extended',
                        'cryptography'],
      entry_points={
          'console_scripts': console_scripts,
          'encadre.frameworks':
          ['flask = encadre_flask:FlaskFramework'],
          'encadre_test_app.controllers':
          ['test_controllers = encadre_test_controllers']
      },
      license='GPLv3')
