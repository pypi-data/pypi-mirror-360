#! /usr/bin/env bash

function bluer_ai_code() {
    if [[ "$abcli_is_mac" == true ]]; then
        /Applications/Visual\ Studio\ Code.app/Contents/Resources/app/bin/code "$@"
    else
        nano "$@"
    fi
}
