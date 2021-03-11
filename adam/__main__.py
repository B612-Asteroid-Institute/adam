import sys
import urllib

import yaml

import adam

DEFAULT_PROD_URL = 'https://pro-equinox-162418.appspot.com/_ah/api/adam/v1'


def config(args):
    cm = adam.ConfigManager()

    # list config
    if args.list:
        print(cm)
        return

    # delete a key
    if args.delete:
        del cm[args.key]
        cm.to_file()
        return

    # set a key
    if args.value is not None:
        cm[args.key] = yaml.safe_load(args.value)
        cm.to_file()
        return

    # print a key
    if args.key is not None:
        *parents, key = args.key.split('.')
        res = {key: cm[args.key]}

        # build a tree (backwards)
        for k in reversed(parents):
            res = {k: res}

        # dump as yaml
        print(yaml.dump(res))
        return

    # print entire config (default action)
    print(cm)


def login(args):
    """Retrieve ADAM credentials."""

    cm = adam.ConfigManager()

    def _do_login(name, url, no_browser):

        # OAuth web flow page
        o = urllib.parse.urlparse(url)
        token_url = f"{o.scheme}://{o.netloc}/token.html"

        print(f"Setting up a configuration named '{name}' for the server: '{url}'.")
        print(f"Please go to {token_url} in your web browser, log in using a GMail or "
              f"GSuite account, and paste your token in this terminal "
              f"(won't be printed to the screen).")
        if not no_browser:
            print("We'll try to automatically open a web browser for you (press ENTER to continue)")
            sys.stdin.readline()

            import webbrowser
            webbrowser.open(token_url)

        # user's credentials
        from getpass import getpass
        refresh_token = getpass("Token: ")

        if refresh_token:
            curr_cfg = None
            try:
                curr_cfg = cm.get_config(name)
            except KeyError:
                print(f'Environment {name} does not exist, creating it')
            if curr_cfg is None:
                curr_cfg = dict(url=url)
            curr_cfg['refresh_token'] = refresh_token
            cm.set_config(name, curr_cfg)
            print(f'Setting default configuration to {name}')
            cm.set_default_env(name)
            cm.to_file()
            print(f'"{name}" configuration updated with new token')

        auth = adam.Auth(adam.AuthenticatingRestProxy(adam.RestRequests()))
        print('Authenticating with ADAM server...')
        if auth.authenticate():
            print(f'{auth.get_user()} authenticated successfully '
                  f'for the "{name}" ADAM configuration')
        else:
            print('Could not authenticate user.')

    if args.name is not None:
        # log into a user-specified service
        _do_login(args.name, args.url, args.no_browser)
    else:
        # log into the default 'prod' environment
        _do_login('prod', DEFAULT_PROD_URL, args.no_browser)


def main(args=None):
    import argparse

    # adamctl
    parser = argparse.ArgumentParser(description='ADAM client command line utility')
    cmds = parser.add_subparsers(title='subcommands', dest='cmd')
    cmds.required = True

    # adamctl config
    config_cmd = cmds.add_parser('config', help='Manage configuration')
    config_cmd.add_argument('-l', '--list', action='store_true', help="show the full configuration")
    config_cmd.add_argument('--delete', action='store_true', help="delete the key")
    config_cmd.add_argument('key', type=str, help="config key to display or set", nargs='?')
    config_cmd.add_argument('value', type=str, help="value to be set, if given", nargs='?')
    config_cmd.set_defaults(func=config)

    # adamctl login
    login_cmd = cmds.add_parser('login', help='Log into an ADAM server')
    login_cmd.add_argument('name', help="name of the upstream ADAM server", nargs='?')
    login_cmd.add_argument('url', help="ADAM server URL", nargs='?')
    login_cmd.add_argument('--no-browser', action='store_true',
                           help="don't try to open a browser, just print the login page URL. "
                                "Useful when logging in on remote machines (e.g., via ssh)"
                           )
    login_cmd.set_defaults(func=login)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    sys.exit(main() or 0)
