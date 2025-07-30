import socket

import click
import requests
import requirements

from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application
from tornado.routing import PathMatches

from packaging.specifiers import SpecifierSet
from packaging.version import Version

MAIN_PYPI = 'https://pypi.org/simple/'
JSON_URL = 'https://pypi.org/pypi/{package}/json'

PACKAGE_HTML = """
<!DOCTYPE html>
<html>
  <head>
    <title>Links for {package}</title>
  </head>
  <body>
    <h1>Links for {package}</h1>
{links}
  </body>
</html>
"""


@click.command()
@click.argument('requirements_file')
@click.option('--port', default=None)
@click.option('--quiet', default=False, is_flag=True)
def main(requirements_file, port, quiet):

    INDEX = requests.get(MAIN_PYPI).content
    INDEX = INDEX.replace(b'href="/simple', b'href="')

    SPECIFIERS = {}
    with open(requirements_file, 'r') as fd:
        for req in requirements.parse(fd):
            if req.specs:
                SPECIFIERS[req.name] = SpecifierSet(','.join([''.join(spec) for spec in req.specs]))

    class MainIndexHandler(RequestHandler):

        async def get(self):
            return self.write(INDEX)

    class PackageIndexHandler(RequestHandler):

        async def get(self, package):

            if package not in SPECIFIERS:
                return self.redirect(MAIN_PYPI + package)

            package_index = requests.get(JSON_URL.format(package=package)).json()

            release_links = ""
            for version, release in package_index['releases'].items():
                if Version(version) in SPECIFIERS[package]:
                    for file in release:
                        if file['requires_python'] is None:
                            release_links += '    <a href="{url}#sha256={sha256}">{filename}</a><br/>\n'.format(
                                url=file['url'], sha256=file['digests']['sha256'], filename=file['filename'])
                        else:
                            rp = file['requires_python'].replace('>', '&gt;')
                            release_links += ('    <a href="{url}#sha256={sha256}" '
                                              'data-requires-python="{rp}">{filename}</a><br/>\n'.format(
                                               url=file['url'], sha256=file['digests']['sha256'],
                                               rp=rp, filename=file['filename']))

            self.write(PACKAGE_HTML.format(package=package, links=release_links))

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 0))
    if port is None:
        port = sock.getsockname()[1]
    sock.close()

    app = Application([(r"/", MainIndexHandler),
                       (PathMatches(r"/(?P<package>\S+)\//?"), PackageIndexHandler)])

    app.listen(port=port)

    if not quiet:
        print(f'Starting PyPIcky server at http://localhost:{port}')

    IOLoop.instance().start()
