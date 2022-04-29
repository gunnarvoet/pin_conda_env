#!/usr/bin/env python
# coding: utf-8

import argparse
import yaml
import subprocess


def parse_input():
    parser = argparse.ArgumentParser(
        description=(
            "Create conda environment file with pinned versions.\n"
            "Conda environment has to be installed."
        )
    )
    parser.add_argument("env_file", help="environment yml file")
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="name output file (default: pinned.yml)",
    )
    args = parser.parse_args()
    return args


def pin_env(env_original, pin_file='pinned.yml'):
    with open(env_original, "r") as ymlfile:
        initial = yaml.safe_load(ymlfile)

    name = initial["name"]

    print(f"pinning environment: {name}")
    process = subprocess.Popen(
        ["conda", "env", "export", "-n", name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()

    exp = yaml.safe_load(stdout)

    frozen = [
        package for package in exp["dependencies"] if type(package) == str
    ]
    frozen_pip = exp["dependencies"][-1]["pip"]

    # Convert frozen env list to dict of packages with version numbers.
    frozen_dict = {}
    for package in frozen:
        [name, version, build] = package.split("=")
        frozen_dict[name] = version

    frozen_dict_pip = {}
    for package in frozen_pip:
        [name, version] = package.split("==")
        frozen_dict_pip[name] = version

    deps = [
        package for package in initial["dependencies"] if type(package) == str
    ]

    deps_pip = initial["dependencies"][-1]["pip"]

    dep_versionized = []
    for dep in deps:
        if type(dep) == str:
            if "=" not in dep:
                if dep in frozen_dict and dep != "pip":
                    dep_versionized.append(f"{dep}={frozen_dict[dep]}")
                else:
                    dep_versionized.append(dep)
            else:
                dep_versionized.append(dep)

    dep_pip_versionized = []
    for dep in deps_pip:
        versionize = True
        if "==" in dep or "@" in dep or "git+" in dep or "hg+" in dep:
            versionize = False
        if versionize:
            if dep in frozen_dict_pip:
                dep_pip_versionized.append(f"{dep}=={frozen_dict_pip[dep]}")
            else:
                dep_pip_versionized.append(dep)
        else:
            dep_pip_versionized.append(dep)

    # add pip dependencies back to the list
    dep_versionized.append(dict(pip=dep_pip_versionized))

    # prepare output dict
    out = initial.copy()

    # add versionized package declarations
    out["dependencies"] = dep_versionized

    with open(pin_file, "w") as file:
        yaml.dump(out, file, default_flow_style=False, sort_keys=False)


if __name__ == "__main__":
    args = parse_input()
    if args.output:
        pin_env(args.env_file, args.output)
    else:
        pin_env(args.env_file)
