# install ttab using `npm i -g ttab`
# on mac, need to change
#   System Prefs -> Security -> Privacy -> Accessibility: add Terminal

# check options for input example file
if [[ "$1" =~ ^(traj|matrix|fes|scan1|frame|ligands|re|cam3t)$ ]]; then
    echo "opening $1 example"
else
    echo "Pleas choose one of traj|matrix|fes|frame|ligands|re|cam3t"
    exit 1
fi

# run client server on port 3333
ttab "cd client; npm run dev;"

# run server in dev mode with reload on port 9023 with chosen example
ttab "cd examples; ./dev_server.sh $1"


