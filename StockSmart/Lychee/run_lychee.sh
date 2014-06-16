. /home/ubuntu/headless.sh

while true; do

sudo rm -rf /tmp/*
. ./kill_all_firefox.sh

python lychee_main.py
sleep 2
#. ./kill_all_firefox.sh
done

