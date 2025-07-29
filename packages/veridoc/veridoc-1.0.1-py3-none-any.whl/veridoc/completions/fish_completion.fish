# VeriDoc Fish Completion Script
# Place in ~/.config/fish/completions/veridoc.fish

# Clear any existing completions
complete -c veridoc -e

# File/directory completion for first argument
complete -c veridoc -n '__fish_is_first_token' -f -a '(__fish_complete_path)'

# Line number completion for second argument (when first is a file)
complete -c veridoc -n '__fish_is_nth_token 2' -f -a '1 10 20 50 100 200 500 1000' -d 'Line number'

# Options
complete -c veridoc -l port -d 'Port to run server on' -x -a '5000 5001 5002 8000 8080 3000'
complete -c veridoc -l no-browser -d 'Start server without opening browser'
complete -c veridoc -l help -d 'Show help message'
complete -c veridoc -l version -d 'Show version information'

# Helper functions
function __fish_is_first_token
    set -l tokens (commandline -poc)
    test (count $tokens) -eq 1
end

function __fish_is_nth_token
    set -l n $argv[1]
    set -l tokens (commandline -poc)
    test (count $tokens) -eq $n
end