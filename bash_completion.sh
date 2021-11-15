#!/usr/bin/env bash

__webtoepub_completion() {

    if [ $COMP_CWORD == 1 ]; then
        COMPREPLY=($(compgen -W "story fetch" -- ${COMP_WORDS[COMP_CWORD]}))
        return
    fi
    
    case ${COMP_WORDS[1]} in
        story) __webtoepub_story_completion ;;
        fetch) __webtoepub_fetch_completion ;;
        *) COMPREPLY=() ;;
    esac

}

__webtoepub_story_completion() {
    if [ $COMP_CWORD == 2 ]; then
        COMPREPLY=($(compgen -W "show list add remove" -- ${COMP_WORDS[2]}))
        return
    fi

    case ${COMP_WORDS[2]} in
        show) __webtoepub_story_handle_completion ;;
        list) __webtoepub_story_list_completion ;;
        add) __webtoepub_story_add_completion ;;
        remove) __webtoepub_story_handle_completion ;;
        *) COMPREPLY=() ;;
    esac
}

__webtoepub_story_handle_completion() {
    if [ $COMP_CWORD -ne 3 ]; then
        COMPREPLY=()
        return
    fi

    local story_handles

    story_handles=`webtoepub story list --name-only | xargs printf "%s "`
    COMPREPLY=($(compgen -W "$story_handles" -- ${COMP_WORDS[3]}))
}

__webtoepub_story_list_completion() {
    if [ $COMP_CWORD -ne 3 ]; then
        COMPREPLY=()
        return
    fi

    COMPREPLY=($(compgen -W "--name-only" -- ${COMP_WORDS[3]}))
}

__webtoepub_story_add_completion() {
    # No real meaningful way to complete anyways, turn it off
    COMPREPLY=()
}

__webtoepub_fetch_completion() {
    if [ $COMP_CWORD == 2 ]; then
        COMPREPLY=($(compgen -W "one all" -- ${COMP_WORDS[2]}))
        return
    fi

    COMPREPLY=()
}