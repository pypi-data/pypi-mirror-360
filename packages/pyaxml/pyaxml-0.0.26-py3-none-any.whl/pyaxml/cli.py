import argparse
import logging
from pathlib import Path
import pyaxml
from pyaxml import conf
try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree


def main() -> int:
    """cli function"""

    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=[
        "axml2xml",
        "xml2axml",
        "arsc2xml"
    ]) 
    parser.add_argument("-i", "--input", help="Specify the apk input file")
    parser.add_argument("-o", "--output", help="Specify the apk output file")
    parser.add_argument("-v", "--version", help="version of pyaxml", action="store_true")

    args = parser.parse_args()

    if args.version:
        print(f"version {conf.VERSION}")
        return 0
    
    if not args.input:
        logging.error("No input provided")
        parser.print_help()
        return 1
    
    if args.command == "axml2xml":
        with open(args.input, "rb") as f:
            # Read AXML
            axml, _ = pyaxml.AXML.from_axml(f.read())
            xml = axml.to_xml()
        # Rewrite the file
        if args.output:
            with open(args.output, "w") as f:
                f.write(etree.tostring(xml, encoding='unicode', pretty_print=True))
        else:
            print(etree.tostring(xml, encoding='unicode', pretty_print=True))
    elif args.command == "xml2axml":
        if not args.output:
            logging.error("No output provided")
            parser.print_help()
            return 1
        with open(args.input, "r") as f:
            # Read XML
            root = etree.fromstring(f.read())
            axml_object = pyaxml.AXML()
            axml_object.from_xml(root)
        # Rewrite the file
        with open(args.output, "wb") as f:
            f.write(axml_object.pack())
    elif args.command == "arsc2xml":
        with open(args.input, "rb") as f:
            # Read AXML
            axml, _ = pyaxml.ARSC.from_axml(f.read())
            xml = axml.list_packages()
        # Rewrite the file
        if args.output:
            with open(args.output, "w") as f:
                f.write(xml)
        else:
            print(xml)
