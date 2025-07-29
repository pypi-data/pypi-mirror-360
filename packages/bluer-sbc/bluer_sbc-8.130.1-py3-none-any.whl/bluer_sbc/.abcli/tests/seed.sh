#! /usr/bin/env bash

function test_bluer_sbc_seed() {
    local options=$1

    local target
    for target in \
        headless_rpi \
        headless_ubuntu_rpi \
        jetson \
        rpi; do
        bluer_ai_eval ,$options \
            bluer_ai_seed $target screen
        [[ $? -ne 0 ]] && return 1
    done

    return 0
}
