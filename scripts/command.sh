#!/bin/bash

# Check if command is specified
if [ -z "$1" ]; then
    echo "Usage: $0 <python_program> <IP1> <IP2> ... <IPn>"
    exit 1
fi

COMMAND=$1

shift # Shift args to manage IP's easily

# IPS from args list
RPIS=("$@")

# Check if at least 1 IP is given
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <command> <IP1> <IP2> ... <IPn>"

    echo "Use default IPs"
    RPIS=("raspberrypiZero1" "raspberrypiZero2" "raspberrypiZero3" "raspberrypiZero4" "raspberrypi" "raspberrypi41" "raspberrypi42" "raspberrypi4L")
fi

USER="trebelge"

SSH_KEY="/home/trebelge/.ssh/id_ed25519"

for HOST in "${RPIS[@]}"; do
    echo "Command $HOST $COMMAND"
    ssh -i "$SSH_KEY" "$USER@$HOST" $COMMAND
done

echo "All commands are launched"