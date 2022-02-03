#!/usr/bin/env bash

__webtoepub_completion() {

    if [ $COMP_CWORD == 1 ]; then
        COMPREPLY=($(compgen -W "story shelf fetch" -- ${COMP_WORDS[COMP_CWORD]}))
        return
    fi
    
    case ${COMP_WORDS[1]} in
        story) __webtoepub_story_completion ;;
        shelf) __webtoepub_shelf_completion ;;
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
        list) __webtoepub_story_list_completion ;;
        show) __webtoepub_story_handle_completion ;;
        remove) __webtoepub_story_handle_completion ;;
        *) COMPREPLY=() ;;
    esac
}

__webtoepub_story_handle_completion() {
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

__webtoepub_shelf_completion() {
    if [ $COMP_CWORD == 2 ]; then
        COMPREPLY=($(compgen -W "show list create delete add remove" -- ${COMP_WORDS[2]}))
        return
    fi

    case ${COMP_WORDS[2]} in
        show) __webtoepub_shelf_handle_completion ;;
        delete) __webtoepub_shelf_handle_completion ;;
        add) __webtoepub_shelf_change_completion ;;
        remove) __webtoepub_shelf_change_completion ;;
        *) COMPREPLY=() ;;
    esac
}

__webtoepub_shelf_handle_completion() {
    local shelf_handles

    shelf_handles=`webtoepub shelf list | xargs printf "%s "`
    COMPREPLY=($(compgen -W "$shelf_handles" -- ${COMP_WORDS[3]}))
}

__webtoepub_shelf_change_completion() {
    if [ $COMP_CWORD == 3 ]; then
        __webtoepub_shelf_handle_completion
        return
    fi

    local story_handles

    story_handles=`webtoepub story list --name-only | xargs printf "%s "`
    COMPREPLY=($(compgen -W "$story_handles" -- ${COMP_WORDS[COMP_CWORD]}))
}

__webtoepub_fetch_completion() {
    if [ $COMP_CWORD == 2 ]; then
        COMPREPLY=($(compgen -W "one all bookshelf" -- ${COMP_WORDS[2]}))
        return
    fi

    if [ $COMP_CWORD == 3 ]; then
        case ${COMP_WORDS[2]} in
            one) __webtoepub_story_handle_completion ;;
            bookshelf) __webtoepub_shelf_handle_completion ;;
            *) COMPREPLY=() ;;
        esac
        return
    fi

    local story_handles

    story_handles=`webtoepub story list --name-only | xargs printf "%s "`
    COMPREPLY=($(compgen -W "$story_handles" -- ${COMP_WORDS[3]}))
}