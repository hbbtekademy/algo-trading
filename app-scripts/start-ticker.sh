#!/bin/sh
export TZ="Asia/Kolkata"
export GOOGLE_CLOUD_PROJECT="mymdapp-dev"
export REDIS_HOST="10.160.0.3"
export REDIS_PORT="6891"

cd $HOME/algo-trading

today=`date +"%Y%m%d"`
server="$HOME/algo-trading/ticker.exe"

until $server; do
        echo "Ticker crashed with error code: $?. Restarting.."
        sleep 1
done

echo "Exiting Ticker start script..."
