import json
import os

if os.getenv('ACES_ROOTDIR') is None:
    raise ValueError("Specify ACES_ROOTDIR environment variable ")
else:
    rootdir = os.environ['ACES_ROOTDIR']

if 'verbose' not in locals():
    verbose = False

with open(f"{rootdir}/pipeline_scripts/default_tclean_commands.json", "r") as fh:
    default_commands = json.load(fh)

with open(f"{rootdir}/pipeline_scripts/override_tclean_commands.json", "r") as fh:
    override_commands = json.load(fh)

commands = default_commands

for sbname,allpars in override_commands.items():
    for partype, replacements in allpars.items():
        for spwsel,tcpars in replacements.items():
            for key, val in tcpars.items():
                if verbose:
                    orig = commands[sbname][partype][spwsel][key]
                    print(f"{sbname} {partype} {spwsel}: {key}: {orig} -> {val}")
                commands[sbname][partype][spwsel][key] = val
            

