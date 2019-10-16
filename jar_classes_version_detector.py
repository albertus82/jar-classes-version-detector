import functools
import logging
import math
import os 
import sys
import zipfile

import urllib.request as urllib2 

proxies = {}

args = []

SCREEN_WIDTH = 70


def print_manifest(jarfile):
    filename = "META-INF/MANIFEST.MF"
    if filename.upper() in (e.upper() for e in jarfile.namelist()):
        print()
        print("".join("-" for _ in range(math.floor(SCREEN_WIDTH / 2 - (len(filename) + 2) / 2))), filename, "".join("-" for _ in range(math.ceil(SCREEN_WIDTH / 2 - (len(filename) + 2) / 2))))
        print(jarfile.read(filename).decode("UTF-8").replace("\r\n", "\n").strip())
        print("".join("-" for _ in range(SCREEN_WIDTH)))


def analyze_classes(jarfile):
    results = {}
    for classname in (e for e in jarfile.namelist() if e.lower().endswith(".class")):
        classbytes = jarfile.read(classname)
        if classbytes[0:4] != b"\xCA\xFE\xBA\xBE":  # Magic word
            print(f"W: Skipping '{classname}' because it isn't a valid Java class file.")
            continue
        minver = int.from_bytes(classbytes[4:6], "big")
        majver = int.from_bytes(classbytes[6:8], "big")
        classes = results.get((majver, minver))
        if classes == None:
            classes = list()
            results[(majver, minver)] = classes
        classes.append(classname)
        logging.debug("%d.%d %s", majver, minver, classname)
    return results


def print_results(results):
    print()
    for version, classes in sorted(results.items(), reverse=True):
        fullver = ".".join(str(e) for e in version)
        javaver = "1." + str(version[0] - 44) if version[0] < 49 else str(version[0] - 44)
        result = f">>> Version {fullver} (Java {javaver}) => {len(classes)} classes found: "
        classnames = functools.reduce(lambda a, b: a + ", " + b, sorted(classes))
        result += classnames[:1000] + '...' if len(classnames) > 1000 else classnames
        result += " <<<"
        print(result)
    print()


def print_separator():
    print()
    print("".join("=" for _ in range(SCREEN_WIDTH)))
    print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        args = sys.argv[1:]
    if len(args) < 1:
        print("E: At least one file name or URL must be provided via command line or 'args' list.")
    try:
        for idx, arg in enumerate(e.strip() for e in args):
            if arg.startswith("http:") or arg.startswith("https:"):
                if len(proxies) > 0:
                    proxy = urllib2.ProxyHandler(proxies)
                    auth = urllib2.HTTPBasicAuthHandler()
                    opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
                    urllib2.install_opener(opener)
                print(f"Downloading: '{arg}'...")
                file = urllib2.urlretrieve(arg)[0]
                print(f"Download completed, created temporary file: '{file}'.")
                jarfilename = arg[arg.rindex("/") + 1:]
            else:
                print(f"Opening: '{arg}'...")
                file = arg
                jarfilename = os.path.basename(file)
            if not zipfile.is_zipfile(file):
                print(f"W: Skipping file '{file}' because it does not exist or is not a valid ZIP file.")
                continue
            print(f"Analyzing: '{jarfilename}'...")
            with zipfile.ZipFile(file) as jarfile:
                print_manifest(jarfile)
                results = analyze_classes(jarfile)
                print_results(results)
            print(f"Analysis of '{jarfilename}' completed.")
            if idx + 1 < len(args):
                print_separator()
    finally:
        logging.info("Cleaning up temporary files...")
        urllib2.urlcleanup()
