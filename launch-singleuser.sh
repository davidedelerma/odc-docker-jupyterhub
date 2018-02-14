#!/bin/sh

echo Bootsrtapping $HOME
touch $HOME/.bootsrtapped
ln -sf /examples $HOME/work/examples
exec jupyterhub-singleuser $@
