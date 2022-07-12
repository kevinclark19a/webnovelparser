#!/usr/bin/env bash

__webnovelparser_completion() {

    if [ $COMP_CWORD == 1 ]; then
        COMPREPLY=($(compgen -W "story shelf fetch" -- ${COMP_WORDS[COMP_CWORD]}))
        return
    fi
    
    case ${COMP_WORDS[1]} in
        story) __webnovelparser_story_completion ;;
        shelf) __webnovelparser_shelf_completion ;;
        fetch) __webnovelparser_fetch_completion ;;
        *) COMPREPLY=() ;;
    esac

}

__webnovelparser_story_completion() {
    if [ $COMP_CWORD == 2 ]; then
        COMPREPLY=($(compgen -W "show list add remove" -- ${COMP_WORDS[2]}))
        return
    fi

    case ${COMP_WORDS[2]} in
        list) __webnovelparser_story_list_completion ;;
        show) __webnovelparser_story_handle_completion ;;
        remove) __webnovelparser_story_handle_completion ;;
        *) COMPREPLY=() ;;
    esac
}

__webnovelparser_story_handle_completion() {
    local story_handles

    story_handles=`webnovelparser story list --name-only | xargs printf "%s "`
    COMPREPLY=($(compgen -W "$story_handles" -- ${COMP_WORDS[3]}))
}

__webnovelparser_story_list_completion() {
    if [ $COMP_CWORD -ne 3 ]; then
        COMPREPLY=()
        return
    fi

    COMPREPLY=($(compgen -W "--name-only" -- ${COMP_WORDS[3]}))
}

__webnovelparser_shelf_completion() {
    if [ $COMP_CWORD == 2 ]; then
        COMPREPLY=($(compgen -W "show list create delete add remove" -- ${COMP_WORDS[2]}))
        return
    fi

    case ${COMP_WORDS[2]} in
        show) __webnovelparser_shelf_handle_completion ;;
        delete) __webnovelparser_shelf_handle_completion ;;
        add) __webnovelparser_shelf_change_completion ;;
        remove) __webnovelparser_shelf_change_completion ;;
        *) COMPREPLY=() ;;
    esac
}

__webnovelparser_shelf_handle_completion() {
    local shelf_handles

    shelf_handles=`webnovelparser shelf list | xargs printf "%s "`
    COMPREPLY=($(compgen -W "$shelf_handles" -- ${COMP_WORDS[3]}))
}

__webnovelparser_shelf_change_completion() {
    if [ $COMP_CWORD == 3 ]; then
        __webnovelparser_shelf_handle_completion
        return
    fi

    local story_handles

    story_handles=`webnovelparser story list --name-only | xargs printf "%s "`
    COMPREPLY=($(compgen -W "$story_handles" -- ${COMP_WORDS[COMP_CWORD]}))
}

__webnovelparser_fetch_completion() {
    if [ $COMP_CWORD == 2 ]; then
        COMPREPLY=($(compgen -W "one all bookshelf" -- ${COMP_WORDS[2]}))
        return
    fi

    if [ $COMP_CWORD == 3 ]; then
        case ${COMP_WORDS[2]} in
            one) __webnovelparser_story_handle_completion ;;
            bookshelf) __webnovelparser_shelf_handle_completion ;;
            *) COMPREPLY=() ;;
        esac
        return
    fi

    local story_handles

    story_handles=`webnovelparser story list --name-only | xargs printf "%s "`
    COMPREPLY=($(compgen -W "$story_handles" -- ${COMP_WORDS[3]}))
}