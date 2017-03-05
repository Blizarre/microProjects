#!/bin/bash

set -e

PROJECT="$1"
PROJECT_ALIGNED="${PROJECT}_aligned"
ACTION="$2"

usage() {
    echo "Perform alignment or crowd removal of all images in the <project> directory"
    echo "the align step will align all images in project with project/reference.jpg and store the aligned image in project_aligned"
    echo "the remove step will merge images in project_aligned into project.jpg"
    echo "Usage:"
    echo "  $1 <project> <align|remove|all>" 1>&2
}



align() {
    local PROJECT="$1"
    local PROJECT_ALIGNED="$2"
    local REFERENCE_FILE="$PROJECT/reference.jpg"

    if ! [ -f "$REFERENCE_FILE" ]; then
        echo "$PROJECT directory must contain a reference file for the aligner: $REFERENCE_FILE" 1>&2
        exit 2
    fi

    rm -fr "$PROJECT_ALIGNED"
    mkdir "$PROJECT_ALIGNED"

    for TO_ALIGN in "$PROJECT/"*; do
        if ! [ "$TO_ALIGN" = "$REFERENCE_FILE" ]; then
            ALIGNED_FILE="$PROJECT_ALIGNED/$(basename "$TO_ALIGN")"
            echo "Aligning $TO_ALIGN to $ALIGNED_FILE ..."
            python aligner.py "$REFERENCE_FILE" "$TO_ALIGN" "$ALIGNED_FILE"
        fi
    done

    cp "$REFERENCE_FILE" "$PROJECT_ALIGNED"
}

remove() {
    local PROJECT="$1"
    local PROJECT_ALIGNED="$2"
    python crowdremover.py -o "${PROJECT}.jpg" "$PROJECT_ALIGNED"/*
}


if [ -z "$PROJECT" ] || ! [ -d "$PROJECT" ] || [ -z "$ACTION" ]; then
    usage $0
    exit 1
fi


[ "$ACTION" = "align" ] && DO_ALIGN=1
[ "$ACTION" = "remove" ] && DO_REMOVE=1
[ "$ACTION" = "all" ] && DO_ALIGN=1 && DO_REMOVE=1

[ -n "$DO_ALIGN" ] && align "$PROJECT" "$PROJECT_ALIGNED"
[ -n "$DO_REMOVE" ] && remove "$PROJECT" "$PROJECT_ALIGNED"
