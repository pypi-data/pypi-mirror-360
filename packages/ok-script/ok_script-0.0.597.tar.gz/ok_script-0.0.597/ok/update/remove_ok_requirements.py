import os
import sys

from ok.update.GitUpdater import remove_ok_requirements

if __name__ == "__main__":
    if '--tag' in sys.argv:
        try:
            tag_index = sys.argv.index('--tag') + 1
            if tag_index < len(sys.argv) and not sys.argv[tag_index].startswith('--'):
                tag_name_arg = sys.argv[tag_index]
            else:
                print("Error: --tag option requires a value.")
                sys.exit(1)
        except ValueError:
            print("Error: --tag option used incorrectly.")
            sys.exit(1)
        repos_index = sys.argv.index('--repos') + 1
        files_index = sys.argv.index('--files') + 1
        # Adjust slicing if --tag is not last
        # This part of arg parsing might need to be more robust if arg order can vary
        repo_urls = sys.argv[repos_index:sys.argv.index('--files')]
        files_filename = sys.argv[sys.argv.index('--files') + 1:sys.argv.index('--tag')]
        if tag_name_arg:  # If --tag was provided and parsed
            print('remove ok_requirements from tag {} cwd {}'.format(tag_name_arg, os.getcwd()))
            remove_ok_requirements(os.getcwd(), tag_name_arg)
