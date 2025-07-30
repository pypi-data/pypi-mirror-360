import argparse
from status_checker.core import check_urls

def main():
    # Initailze the argument parser
    parser = argparse.ArgumentParser(
        description='HTTPS Status Checker CLI'
    )
    # Add a mutually exclusive group to the parser
    # Only one argument can be used at a time
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--urls', nargs='+', help='List of URLs to check status.')
    group.add_argument('--file', help='Path of file containing URLs to checked.')
    
    # Add another optional argument to accept file path where to write the result
    parser.add_argument('--output', help='File path where to write the results.')
    
    args = parser.parse_args()
    
    # Check if user provided the input file
    if args.file:
        # Open the file and read the URLs
        try:
            with open(args.file, 'r') as f:
                urls = [line.strip for line in f if line.strip()]
        except Exception as e:
            print(f'Error reading file: {e}')
            return
    else:
        urls = args.urls
        
    # Check URLs
    results = check_urls(urls)
    
    for result in results:
        print(result)
        
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write('\n'.join(results))
        except Exception as e:
            print(f'Error writing results to file: {e}')
            return
