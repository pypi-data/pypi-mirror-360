"""Module download_retry"""

import argparse
import time
import sys
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

__version__ = "0.1.2"


def str2bool(value: str) -> bool:
    """ str2bool """
    return value.lower() in ('yes', 'true', 't', '1')


def download_file(url: str, output_file: str, insecure: bool) -> bool:
    """ download_file """
    try:
        response = requests.get(url, timeout=10, verify=not insecure)
        if response.status_code == 200:
            with open(output_file, 'wb') as f:
                f.write(response.content)
            return True
        return False
    except requests.RequestException:
        return False


def main() -> None:
    """ main """
    parser = argparse.ArgumentParser(description="Retry downloading binary file from webpage.")
    parser.add_argument('--version', action='version', version=f"%(prog)s {__version__}")
    parser.add_argument('--url', required=True, help='Webpage URL to download')
    parser.add_argument('--delta_t', type=int, required=True, help='Retry interval in seconds')
    parser.add_argument('--max_t', type=int, required=True, help='Maximum wait time in seconds')
    parser.add_argument('--out', required=True, help='Output filename')
    parser.add_argument('--insecure', type=str2bool, default=True,
                        help='Skip SSL certificate verification (default: True)')

    args = parser.parse_args()

    start_time = time.time()
    elapsed = 0.0

    while elapsed < args.max_t:
        success: bool = download_file(args.url, args.out, args.insecure)
        if success:
            print(f"Downloaded successfully to {args.out}")
            sys.exit(0)
        time.sleep(args.delta_t)
        elapsed = time.time() - start_time

    print(f"Failed to download within {args.max_t} seconds.", file=sys.stderr)
    sys.exit(1)


if __name__ == '__main__':
    main()
