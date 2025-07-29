#compdef veridoc

# VeriDoc Zsh Completion Script
# Add to ~/.zshrc or place in a directory in $fpath

_veridoc() {
    local context state line
    typeset -A opt_args
    
    _arguments \
        '1:file or directory:_files' \
        '2:line number:_line_numbers' \
        '--port[Port to run server on]:port:_ports' \
        '--no-browser[Start server without opening browser]' \
        '--help[Show help message]' \
        '--version[Show version information]'
}

_line_numbers() {
    local expl
    local -a line_numbers
    line_numbers=(1 10 20 50 100 200 500 1000)
    _describe 'line numbers' line_numbers
}

_ports() {
    local expl
    local -a ports
    ports=(5000 5001 5002 8000 8080 3000 4000 9000)
    _describe 'ports' ports
}

_veridoc "$@"