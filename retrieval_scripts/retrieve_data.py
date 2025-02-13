import numpy as np
from astroquery.alma import Alma
import requests
import six
import os
import sys

if len(sys.argv) > 1:
    username = sys.argv[1]
    print(f"Using username {username}")
else:
    username = six.moves.input("Username: ")

for server_url in ('https://almascience.eso.org', 'https://almascience.nrao.edu', 'https://almascience.nao.ac.jp'):
    print(f"Logging in to ALMA at server {server_url}", flush=True)
    try:
        alma = Alma()
        alma.TIMEOUT = 300
        # if the NRAO server is too slow...
        alma.archive_url = server_url
        alma.dataarchive_url = server_url
        alma.cache_location = Alma.cache_location = '.'
        alma.login(username)
        print(f"Logged in as {username}", flush=True)

        results = alma.query(payload=dict(project_code='2021.1.00172.L'), public=None, cache=False)

        release_dates = results['obs_release_date']
        # remove all 3000- dates
        ok_release_dates = np.array([int(x[0]) < 3 for x in release_dates])
        results = results[ok_release_dates]

        obsids = np.unique(results['obs_id'])

        # these obs IDs are broken - ALMA will index their data but they are not hosted
        bad_obsids = [f'uid://A001/X15a0/{x}' for x in ('X174', 'X17c', 'Xea', 'X1a4', 'X134', 'X17c', 'X138', 'X17a')]

        obsids = list(set(obsids) - set(bad_obsids))

        data = alma.retrieve_data_from_uid(obsids)

        break
    except requests.exceptions.ReadTimeout as ex:
        # try again w/a different sserver
        print(ex)
        continue
    except requests.exceptions.HTTPError as ex:
        print(ex)
        continue


# Optional: %run retrieve_data <username> True will extract files
if len(sys.argv) > 2:
    extract = bool(sys.argv[2])
else:
    extract = False

if extract:
    import tarfile
    for fn in data:
        if fn.endswith('.tar'):
            print(f"Extracting {fn}")
            with tarfile.TarFile(fn) as tf:
                for member in tf.getmembers():
                    if not os.path.exists(member.name):
                        tf.extract(member)
