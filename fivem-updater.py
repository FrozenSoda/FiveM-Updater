#!/usr/bin/env python3

import argparse
import os
import time
import tarfile
import datetime


class ServerBuild:
    def __init__(self, build_num, download_url):
        self.build_num = build_num
        self.download_url = download_url


def get_latest_server_build():
    build_page = requests.get('https://runtime.fivem.net/artifacts/fivem/build_proot_linux/master/').text
    build_page = BeautifulSoup(build_page, features='html.parser')

    download_recommended_btn = [a for a in build_page.find_all('a') if 'RECOMMENDED' in a.text.upper()][0]
    download_url = download_recommended_btn['href']  # Relative URL
    build_num = download_url.split('/')[1].split('-')[0]
    download_url = download_url.replace('.', 'https://runtime.fivem.net/artifacts/fivem/build_proot_linux/master',
                                        1)  # Absolute URL

    return ServerBuild(build_num, download_url)


def get_installed_build_num(server_dir):
    version_file = os.path.join(server_dir, 'FXServer/server/.fsu-version')
    if os.path.isfile(version_file):
        with open(version_file, 'r') as f:
            content = f.readlines()
            return [line for line in content if not line.startswith('#')][0]
    return None


def untar_safe(archive_file, destination):
    with tarfile.open(archive_file) as a:
        for member in a.getnames():
            real_path = os.path.realpath(os.path.join(destination, member))
            if real_path.startswith(os.path.realpath(destination)):
                a.extract(member, destination)
            else:
                raise Exception('ERROR: Tar extraction cancelled for security reasons due to unsafe '
                                'archive member name. Is the archive malicious?')


def generate_vacant_dir_path(dir):
    dir_base = (dir if not dir.endswith('/') else dir[:-1])
    i = 2
    while os.path.isdir(dir):
        dir = dir_base + '.' + str(i)
        i += 1
    return dir


def update_server_binaries(server_dir, latest_build, installed_build_num):
    def sizeof_fmt(num, suffix='B'):
        for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
            if abs(num) < 1024.0:
                return "%3.1f %s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f %s%s" % (num, 'Yi', suffix)

    server_binary_dir = os.path.join(server_dir, 'FXServer/server')

    if not os.path.isdir(server_dir):
        os.mkdir(server_dir)
    if not os.path.isdir(os.path.join(server_dir, 'FXServer')):
        os.mkdir(os.path.join(server_dir, 'FXServer'))
    if not os.path.isdir(server_binary_dir):
        os.mkdir(server_binary_dir)

    headers = requests.head(latest_build.download_url)
    download_size = int(headers.headers['Content-Length'])
    print('Update download size: {}'.format(sizeof_fmt(download_size)))

    print('Downloading update archive ...')

    if not os.path.isdir(os.path.expanduser('~/FiveM-Server-Archives')):
        os.mkdir(os.path.expanduser('~/FiveM-Server-Archives'))

    download_request = requests.get(latest_build.download_url)
    archive_file = os.path.expanduser('~/FiveM-Server-Archives/{}.tar.xz'.format(latest_build.build_num))
    with open(archive_file, 'wb') as f:
        f.write(download_request.content)

    if installed_build_num is not None:
        dest = os.path.join(server_binary_dir, os.pardir, '.server.{}'.format(installed_build_num))
        dest = generate_vacant_dir_path(dest)
        os.rename(server_binary_dir, dest)
    else:
        dest = os.path.join(server_binary_dir, os.pardir, '.server.{}'
                            .format(datetime.date.today().strftime('%Y.%m.%d')))
        dest = generate_vacant_dir_path(dest)
        os.rename(server_binary_dir, dest)

    print('Extracting archive ...')
    untar_safe(archive_file, server_binary_dir)

    version_file = os.path.join(server_binary_dir, '.fsu-version')
    with open(version_file, 'w') as f:
        f.write('# FiveM Server Updater Version Data File.\n')
        f.write('# This file contains the build number of the installed FiveM server build, '
                'which is used by the updater script.\n')
        f.write('# Do NOT modify the contents of this file.\n')
        f.write(latest_build.build_num)


def update_cfx_server_data(server_dir):
    server_data_dir = os.path.join(server_dir, 'FXServer/server-data')

    if not os.path.isdir(server_data_dir):
        os.mkdir(server_data_dir)

    if len(os.listdir(server_data_dir)) == 0:
        print('Cloning cfx-server-data ...')
        git.Repo.clone_from('https://github.com/citizenfx/cfx-server-data.git', server_data_dir)
    else:
        print('Pulling updates for cfx-server-data ...')
        g = git.Git(server_data_dir)
        g.pull()


def pushover(app_token, user_key, message, title, call_is_a_retry=False):
    import http.client
    import urllib

    conn = http.client.HTTPSConnection('api.pushover.net:443')
    conn.request('POST', '/1/messages.json',
                 urllib.parse.urlencode({
                     'token': app_token,
                     'user': user_key,
                     'message': message,
                     'title': title,
                 }), {'Content-type': 'application/x-www-form-urlencoded'})
    response = conn.getresponse()
    if response.status == 200:
        # No error
        return True
    elif str(response.status).startswith('4'):
        raise Exception('ERROR: Pushover POST returned status code {}'.format(response.status))
    else:
        if call_is_a_retry:
            return False

        # Unable to connect to API
        attempts = 5
        for i in range(1, attempts):
            wait = 10 * i
            print('Unable to connect to Pushover API, retrying in {} seconds ...'.format(wait))
            time.sleep(wait)
            if pushover(app_token, user_key, message, title, True):
                return True
        print('ERROR: Unable to connect to Pushover API. Now giving up after {} failed attempts.'.format(attempts))
        return False


def main(args):
    if (args.pushover_app_token is not None and args.pushover_user_key is None) or \
            (args.pushover_app_token is None and args.pushover_user_key is not None):
        print('ERROR: Both pushover-app-token and pushover-user-key must be specified, or neither.')
        return False
    elif args.pushover_app_token is not None:
        print('Pushover notifications are enabled.')
    else:
        print('Pushover notifications are disabled. Specify pushover-app-token and pushover-user-key to enable.')
    if args.server_dir is None and not args.check_only:
        print('Server directory is omitted, running in check-only mode.')

    print('Retrieving build data ...')
    latest_build = get_latest_server_build()
    print('Latest recommended build: {}'.format(latest_build.build_num))

    if args.server_dir is None:
        return

    installed_build_num = get_installed_build_num(args.server_dir)
    print('Installed build: ........ {}'.format(installed_build_num if installed_build_num is not None else 'Unknown'))

    if args.check_only:
        return

    if installed_build_num is None or latest_build.build_num > installed_build_num or args.force_update:
        update_server_binaries(args.server_dir, latest_build, installed_build_num)
        update_cfx_server_data(args.server_dir)
        print('Update finished.')
    else:
        update_cfx_server_data(args.server_dir)
        print('cfx-server-data update finished.')
        print('You are running the latest recommended server build. Update of server binaries is not required.')

    if not os.path.isfile(os.path.join(args.server_dir, 'FXServer/server-data/server.cfg')):
        print('\nNote: You need to set up server.cfg before starting the server. '
              'Consult this guide: https://docs.fivem.net/docs/server-manual/setting-up-a-server/')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update FiveM server effortlessly.')
    parser.add_argument('--server-dir',
                        help='The full path to the directory where the \'FXServer\' directory resides.')
    parser.add_argument('--check-only', action='store_true',
                        help='Only retrieve the latest build and, if server-dir is specified, the installed build. '
                             'Do not update server binaries nor cfx-server-data.')
    parser.add_argument('--force-update', action='store_true',
                        help='Update server binaries even if the latest build is already installed.')
    parser.add_argument('--pushover-app-token',
                        help='Your Pushover app token, which you can specify to be notified of errors on your phone.')
    parser.add_argument('--pushover-user-key',
                        help='Your Pushover user key, which you can specify to be notified of errors on your phone.')
    args = parser.parse_args()

    if args.server_dir is not None:
        args.server_dir = os.path.expanduser(args.server_dir)

    try:
        import requests
        from bs4 import BeautifulSoup
        import git

        main(args)
    except Exception as e:
        pushover(args.pushover_app_token, args.pushover_user_key, str(e), 'FiveM Server Update Failed')
        raise e
