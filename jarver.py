import functools
import io
import logging
import math
import os
import sys
import zipfile

import urllib.request as urllib2

SCREEN_WIDTH = 70

MAX_RESULT_LENGTH = 1000

proxies = {
    # "http": "http://username:password@address:port",
    # "https": "http://username:password@address:port"
}

args = []


def print_manifest(archive):
    filename = "META-INF/MANIFEST.MF"
    if filename.upper() in (e.upper() for e in archive.namelist()):
        print()
        print("".join("-" for _ in range(math.floor(SCREEN_WIDTH / 2 - (len(filename) + 2) / 2))), end=" ")
        print(filename, end=" ")
        print("".join("-" for _ in range(math.ceil(SCREEN_WIDTH / 2 - (len(filename) + 2) / 2))))
        print(archive.read(filename).decode("UTF-8").replace("\r\n", "\n").strip())
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
        print(f"Warning! Skipping file '{file}' because it does not exist or is not a valid ZIP archive.")
    else:
        print(f"Analyzing archive: '{display_name}'...")
        with zipfile.ZipFile(file) as archive:
            print_manifest(archive)
            results = analyze_contents(archive)
            print_results(results)
        print(f"Analysis of archive '{display_name}' completed.")


def analyze_nested_file(file, display_name, level):
    if not file.seekable():  # Only to ensure compatibility with Python <3.7
        file = io.BytesIO(file.read())
    print()
    if not zipfile.is_zipfile(file):
        print(f"Warning! Skipping nested file '{display_name}' (level {level}) because it is not a valid ZIP archive.")
    else:
        print(f"Analyzing nested archive: '{display_name}' (level {level})...")
        with zipfile.ZipFile(file) as archive:
            results = analyze_contents(archive, level)
            print_results(results, level)
        print(f"Analysis of nested archive '{display_name}' (level {level}) completed.")


def analyze_contents(archive, level=0):
    results = {}
    for classname in (e for e in archive.namelist() if e.lower().endswith(".class")):
        classbytes = archive.read(classname)
        if classbytes[0:4] != b"\xCA\xFE\xBA\xBE":  # Magic word
            print(f"Warning! Skipping '{classname}' because it isn't a valid Java class file.")
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
        analyze_nested_file(archive.open(nested), nested, level + 1)

    return results


def print_results(results, level=0):
    print()
    if len(results) > 0:
        ELLIPSIS = "..."
        TERMINATOR = " <<<"
        max_line_length = MAX_RESULT_LENGTH if level == 0 else SCREEN_WIDTH
        for version, classes in sorted(results.items(), reverse=True):
            fullver = ".".join(str(e) for e in version)
            javaver = "1." + str(version[0] - 44) if version[0] < 49 else str(version[0] - 44)
            classes_count = len(classes)
            result = f">>> Version {fullver} (Java {javaver}) => "
            result += f"{classes_count} {'class' if classes_count == 1 else 'classes'} found: "
            result += functools.reduce(lambda a, b: a + ", " + b, sorted(classes))
            if len(result) >= max_line_length - len(TERMINATOR):
                result = result[:max_line_length - len(TERMINATOR) - len(ELLIPSIS)] + ELLIPSIS
            result += TERMINATOR
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
        print("Error! At least one file name or URL must be provided via command line or 'args' list.")
    try:
        for idx in range(len(argv)):
            process_arg(argv, idx)
    finally:
        logging.info("Cleaning up temporary files...")
        urllib2.urlcleanup()


if __name__ == "__main__":
    main(sys.argv[1:] if len(sys.argv) > 1 else args)
