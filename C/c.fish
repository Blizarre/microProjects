# Requires the packages `sponge` (usually in moreutils) and `fzf` (usually in its own package)

# This script will use the following files:
# - ~/paths: An index of all the dirs to use for autocomplete
# - ~/paths.history: An index of all the directories that have been visited recently
# - ~/paths.ignore: a list of regex that can be used to filter out entries from the index in ~/paths [Optional]

function __c_add_path_history -a dir
    # keep the history of the last 100 unique directories visited
    set dir (readlink -f $dir)
    grep -v $dir ~/paths.history | head -n 100 | sponge ~/paths.history
    echo $dir >>~/paths.history
end

function C -w cd -d "cd on steroids for your previously visited directories"
    set dir (cat ~/paths.history | fzf --tiebreak=end --query=$argv)
    if test -n "$dir"
        __c_add_path_history $dir
        cd $dir
    end
end

function c -w cd -d "cd on steroids for your filesystem"
    # -s will rebuild the directory index
    if string match -a -- -s $argv >/dev/null
        echo "Regenerating the sources index"
        # pretty unintuitive: we select everything that we do not want first, _then_ we say "or print" which
        # invert the selection and display everything else. -prune is there to prevent "find" from going
        # into the subdirectories.
        find ~/ \
            -name '.git' -prune \
            # Rust's cargo build dir
            -o -name target -prune \
            # Nodejs modules dir
            -o -name node_modules -prune \
            # Python's env dirs
            -o -name venv -prune \
            -o -name site-package -prune \
            -o -name '.venv' -prune \
            -o -not -type d -o -print >~/paths
        # Then we remove any line in the path file that match any line in the ~/paths.ignore file
        if test -f ~/paths.ignore
            for line in $(cat ~/paths.ignore)
                grep -E -v $line ~/paths | sponge ~/paths
            end
        end
        return
    else
        # If the directory exist go there (like cd)
        if test -d "$argv"
            set dir $argv
            # Otherwise display the fzf UI
        else
            set dir (cat ~/paths | fzf --query=$argv)
        end
    end
    # If we are supposed to go somewhere ($dir not empty), go there and save
    # a new entry in the history file
    if string length $dir >/dev/null
        __c_add_path_history $dir
        cd $dir
    end
end
