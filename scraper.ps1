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
    echo "  crawl         Downloads the chapters by crawling"
    echo "  download      Downloads the chapters"
    echo "  parse         Parses the chapters"
    echo "  build         Builds the books"
    echo "  start         Starts the FlareSolver server"
    echo "  stop          Stops the FlareSolver server"
    echo "  logs          Prints the FlareSolver server logs"
}

$Command = $args[0]
switch -Exact ($Command)
{
    'info' { python $libDir\get_book_info.py $args[1..($args.Count)] }
    'crawl' { python $LibDir\crawl.py $args[1..($args.Count)] }
    'download' { python $LibDir\download.py $args[1..($args.Count)] }
    'parse' { python $LibDir\parse_chapters.py $args[1..($args.Count)] }
    'build' {python $LibDir\make_book.py $args[1..($args.Count)] }
    'start' { 
        $cwd = "$(pwd)"
        cd $SrcDir
        docker compose up -d
        cd $cwd
    }
    'stop' { 
        $cwd = "$(pwd)"
        cd $SrcDir
        docker compose down
        cd $cwd
    }
    'logs' { 
        $cwd = "$(pwd)"
        cd $SrcDir
        docker compose logs -f
        cd $cwd
    }
    'rename' {python $LibDir\rename.py $args[1..($args.Count)] }
    Default { print_usage }
}

deactivate
