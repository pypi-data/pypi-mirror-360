#! /usr/bin/env bash

function test_bluer_ugv_help() {
    local options=$1

    local module
    for module in \
        "@ugv" \
        \
        "@ugv pypi" \
        "@ugv pypi browse" \
        "@ugv pypi build" \
        "@ugv pypi install" \
        \
        "@ugv pytest" \
        \
        "@ugv test" \
        "@ugv test list" \
        \
        "bluer_ugv"; do
        bluer_ai_eval ,$options \
            bluer_ai_help $module
        [[ $? -ne 0 ]] && return 1

        bluer_ai_hr
    done

    return 0
}
