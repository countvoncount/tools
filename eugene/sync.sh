STORE="$1"

[ -z "$STORE" ] && echo '*** Needs store id' >&2 && exit 1

FILECACHE='~/vurve/data/sophie/filecache'

mkdir -p "${FILECACHE}/${STORE}"
nice rsync -rv deployadmin@sophie1:"/palaran/data/sophie/filecache/${STORE}/" "${FILECACHE}/${STORE}"



