#!/bin/sh
export TZ="Asia/Kolkata"
export GOOGLE_CLOUD_PROJECT="mymdapp-dev"
export REDIS_RT_HOST="10.160.0.3"
export REDIS_RT_PORT="6892"

# shellcheck disable=SC2086
cd $HOME/algo-trading || { echo "Failure. Could not cd into directory "; exit 1;}

server="$HOME/algo-trading/candle-generator.exe"

until $server; do
        echo "Ticker crashed with error code: $?. Restarting.."
        sleep 1
done

echo "Exiting Ticker start script..."
