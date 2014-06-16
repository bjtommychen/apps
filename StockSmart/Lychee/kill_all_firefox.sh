 ps aux | grep 'firefox/firefox' | awk '{print $2}' | xargs sudo kill -9

