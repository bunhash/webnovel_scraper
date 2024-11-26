# Powershell
#
# @author bunhash
# @email bunhash@bhmail.me
#
# Powershell wrapper to the scraper
#

$SrcPath = $script:MyInvocation.MyCommand.Path
$SrcDir = Split-Path -Parent $SrcPath
$LibDir = "$SrcDir\lib"
$VenvDir = "$SrcDir\venv"
. $VenvDir\Scripts\activate.ps1

function print_usage
{
    echo "usage: script.ps1 <command> [arg...]"
    echo ""
    echo "COMMANDS"
    echo "  info [URL]    Gets the book info"
    echo "  download      Downloads the chapters"
    echo "  parse         Parses the chapters"
    echo "  build         Builds the books"
}

$Command = $args[0]
switch -Exact ($Command)
{
    'info' { python $libDir\get_book_info.py $args[1] }
    'download' { type .\urlcache.txt | python $LibDir\download.py }
    'parse' { type .\urlcache.txt | python $LibDir\parse_chapters.py }
    'build' {python $LibDir\make_book.py }
    Default { print_usage }
}

deactivate
