import logging
import argparse
import run

logging.basicConfig(level=logging.INFO)


def main(cpp_driver_git, scylla_install_dir, versions, protocols):
    results = []
    for version in versions:
        for protocol in protocols:
            logging.info('=== CPP DRIVER VERSION {}, PROTOCOL v{} ==='.format(version, protocol))
            results.append(run.Run(cpp_driver_git, scylla_install_dir, version, protocol))

    logging.info('=== CPP DRIVER MATRIX RESULTS ===')
    status = 0
    for result in results:
        logging.info(result)
        if result.summary['failure'] > 0:
            status = 1
    quit(status)

if __name__ == '__main__':
    versions = ['master']
    protocols = ['3', '4']
    parser = argparse.ArgumentParser()
    parser.add_argument('cpp_driver_git', help='folder with git repository of cpp-driver')
    parser.add_argument('scylla_install_dir',
                        help='folder with scylla installation, e.g. a checked out git scylla has been built')
    parser.add_argument('--versions', default=versions,
                        help='cpp-driver versions to test, default={}'.format(','.join(versions)))
    parser.add_argument('--protocols', default=protocols,
                        help='cqlsh native protocol, default={}'.format(','.join(protocols)))
    arguments = parser.parse_args()
    if not isinstance(arguments.versions, list):
        versions = arguments.versions.split(',')
    if not isinstance(arguments.protocols, list):
        protocols = arguments.protocols.split(',')
    main(arguments.cpp_driver_git, arguments.scylla_install_dir, versions, protocols)
