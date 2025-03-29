#!/bin/bash


# IPS from args list
RPIS=("$@")

# Check if at least 1 IP is given
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <IP1> <IP2> ... <IPn>"

    echo "Use default IPs"
    RPIS=("raspberrypi" "raspberrypi4L" "raspberrypiZero1" "raspberrypiZero2" "raspberrypiZero3" "raspberrypiZero4")
fi

LOCAL_DIR="/home/trebelge/OneDrive/Cours UCL/Thesis/Balboa_network/RPi"
REMOTE_DIR="/home/trebelge/Documents/Balboa_Network"

USER="trebelge"

SSH_KEY="/home/trebelge/.ssh/id_ed25519"

for HOST in "${RPIS[@]}"; do
    echo "Removing old directory on $HOST..."
    ssh -i "$SSH_KEY" "$USER@$HOST" "rm -rf $REMOTE_DIR"

    echo "Transfer of files to $HOST..."
    scp -i "$SSH_KEY" -r "$LOCAL_DIR" "$USER@$HOST:$REMOTE_DIR"
done

echo "All transfers are done"