#!/bin/sh

export DIR=$(dirname $0)

if [ -n $XDG_DATA_HOME ]; then
  export XDG_DATA_HOME=$HOME/.local/share
fi

echo $DIR
echo $XDG_DATA_HOME
cp $DIR/wraptor.plugin $XDG_DATA_HOME/gedit/plugins/
cp $DIR/wraptor.py $XDG_DATA_HOME/gedit/plugins/
echo "done"
