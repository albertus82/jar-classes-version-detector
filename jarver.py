import functools
import logging
import math
import os
import sys
import zipfile

import urllib.request as urllib2

SCREEN_WIDTH = 70

proxies = {
    # "http": "http://username:password@address:port",
    # "https": "http://username:password@address:port"
}

args = []


def print_manifest(jarfile):
    filename = "META-INF/MANIFEST.MF"
    if filename.upper() in (e.upper() for e in jarfile.namelist()):
        print()
        print("".join("-" for _ in range(math.floor(SCREEN_WIDTH / 2 - (len(filename) + 2) / 2))), end=" ")
        print(filename, end=" ")
        print("".join("-" for _ in range(math.ceil(SCREEN_WIDTH / 2 - (len(filename) + 2) / 2))))
        print(jarfile.read(filename).decode("UTF-8").replace("\r\n", "\n").strip())
        print("".join("-" for _ in range(SCREEN_WIDTH)))


def download(arg):
    if len(proxies) > 0:
        proxy = urllib2.ProxyHandler(proxies)
        auth = urllib2.HTTPBasicAuthHandler()
        opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
        urllib2.install_opener(opener)
    print(f"Downloading: '{arg}'...")
    file = urllib2.urlretrieve(arg)[0]
    print(f"Download completed, created temporary file: '{file}'.")
    return file


def analyze_file(file, display_name):
    if not zipfile.is_zipfile(file):
        print(f"Warning: Skipping file '{file}' because it does not exist or is not a valid ZIP file.")
    else:
        print(f"Analyzing: '{display_name}'...")
        with zipfile.ZipFile(file) as archive:
            print_manifest(archive)
            results = analyze_contents(archive)
            print_results(results)
        print(f"Analysis of '{display_name}' completed.")


def analyze_contents(archive):
    results = {}
    for classname in (e for e in archive.namelist() if e.lower().endswith(".class")):
        classbytes = archive.read(classname)
        if classbytes[0:4] != b"\xCA\xFE\xBA\xBE":  # Magic word
            print(f"W: Skipping '{classname}' because it isn't a valid Java class file.")
            continue
        minver = int.from_bytes(classbytes[4:6], "big")
        majver = int.from_bytes(classbytes[6:8], "big")
        classes = results.get((majver, minver))
        if classes is None:
            classes = list()
            results[(majver, minver)] = classes
        classes.append(classname)
        logging.debug("%d.%d %s", majver, minver, classname)

    # Check for nested archives (EAR/WAR/fat JAR)
    for nested in (e for e in archive.namelist() if (
            e.lower().endswith(".jar") or
            e.lower().endswith(".war") or
            e.lower().endswith(".ear") or
            e.lower().endswith(".rar")
        )):
        print()
        print(f"Detected nested archive: '{nested}'")
        analyze_file(archive.open(nested), nested)

    return results


def print_results(results):
    print()
    if len(results) > 0:
        for version, classes in sorted(results.items(), reverse=True):
            fullver = ".".join(str(e) for e in version)
            javaver = "1." + str(version[0] - 44) if version[0] < 49 else str(version[0] - 44)
            result = f">>> Version {fullver} (Java {javaver}) => {len(classes)} classes found: "
            classnames = functools.reduce(lambda a, b: a + ", " + b, sorted(classes))
            result += classnames[:1000] + '...' if len(classnames) > 1000 else classnames
            result += " <<<"
            print(result)
    else:
        print("No Java class found.")
    print()


def print_separator():
    print()
    print("".join("=" for _ in range(SCREEN_WIDTH)))
    print()


def process_arg(argv, idx):
    arg = argv[idx].strip()
    if arg.startswith("http:") or arg.startswith("https:"):
        file = download(arg)
        display_name = arg[arg.rindex("/") + 1:]
    else:
        print(f"Opening: '{arg}'...")
        file = arg
        display_name = os.path.basename(file)
    analyze_file(file, display_name)
    if idx + 1 < len(argv):
        print_separator()


def main(argv):
    if len(argv) < 1:
        print("Error: At least one file name or URL must be provided via command line or 'args' list.")
    try:
        for idx in range(len(argv)):
            process_arg(argv, idx)
    finally:
        logging.info("Cleaning up temporary files...")
        urllib2.urlcleanup()


if __name__ == "__main__":
    main(sys.argv[1:] if len(sys.argv) > 1 else args)
