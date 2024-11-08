#!/bin/bash
#
# @author bunhash
# @email bunhash@bhmail.me
#
# Bash wrapper to the scraper
#

SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
LIB_DIR="${SRC_DIR}/lib"
VENV_DIR="${SRC_DIR}/venv"
source "${VENV_DIR}/bin/activate"

print_usage() {
    echo "usage: scraper.sh <command> [arg...]"
    echo ""
    echo "COMMANDS"
    echo "  info [URL]    Gets the book info"
    echo "  download      Downloads the chapters"
    echo "  parse         Parses the chapters"
    echo "  build         Builds the books"
}

COMMAND="$1"
shift
case "${COMMAND}" in
    info)
        python "${LIB_DIR}/get_book_info.py" "$@"
        ;;
    download)
        python "${LIB_DIR}/download.py"
        ;;
    parse)
        python "${LIB_DIR}/parse_chapters.py"
        ;;
    build)
        python "${LIB_DIR}/make_book.py"
        ebook-convert "$(head -n1 bookinfo.txt).epub" "$(head -n1 bookinfo.txt).azw3" --no-inline-toc
        ;;
    *)
        print_usage
        ;;
esac
