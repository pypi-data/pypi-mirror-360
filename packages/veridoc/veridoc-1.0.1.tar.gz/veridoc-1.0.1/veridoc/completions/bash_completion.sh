#!/bin/bash
# VeriDoc Bash Completion Script
# Add to ~/.bashrc or /etc/bash_completion.d/veridoc

_veridoc_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Available options
    opts="--port --no-browser --help --version"
    
    case "${prev}" in
        --port)
            # Suggest common port numbers
            COMPREPLY=( $(compgen -W "5000 5001 5002 8000 8080 3000" -- ${cur}) )
            return 0
            ;;
        veridoc)
            # First argument - suggest files and directories
            if [[ ${cur} == -* ]] ; then
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
                return 0
            else
                # Complete files and directories
                COMPREPLY=( $(compgen -f -- ${cur}) )
                return 0
            fi
            ;;
        *)
            # Subsequent arguments
            if [[ ${cur} == -* ]] ; then
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
                return 0
            else
                # If previous argument is a file, suggest line numbers
                if [[ -f "${prev}" ]]; then
                    # Suggest common line numbers
                    COMPREPLY=( $(compgen -W "1 10 20 50 100" -- ${cur}) )
                else
                    # Complete files and directories
                    COMPREPLY=( $(compgen -f -- ${cur}) )
                fi
                return 0
            fi
            ;;
    esac
}

# Register completion function
complete -F _veridoc_completion veridoc

# Also complete for ./veridoc if run from project directory
complete -F _veridoc_completion ./veridoc