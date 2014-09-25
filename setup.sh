#!/bin/bash

echo "YOU SHOULD DO THIS IN A VENV AND IN A DIRECTORY YOU CAN TRASH"
echo "This will clone a repo and install from an experimental branch"
read -r -p "Continue?? [y/N] " response

case $response in
    [yY][eE][sS]|[yY]) : ;;
    *) exit 0 ;;
esac

git clone https://github.com/eredding-rmn/acky.git
pushd acky
git checkout -b instancestatus origin/instancestatus
python setup.py install
popd
echo "ENJOYYYYYY"

