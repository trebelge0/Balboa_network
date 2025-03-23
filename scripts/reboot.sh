#!/bin/bash


# IPS from args list
RPIS=("$@")

# Check if at least 1 IP is given
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <IP1> <IP2> ... <IPn>"

    echo "Use default IPs"
    RPIS=("raspberrypi" "raspberrypi4L" "raspberrypiZero1" "raspberrypiZero2" "raspberrypiZero3" "raspberrypiZero4")
fi

USER="trebelge"

SSH_KEY="/home/trebelge/.ssh/id_ed25519"

for HOST in "${RPIS[@]}"; do
    echo "Reboot $HOST..."
    ssh -i "$SSH_KEY" "$USER@$HOST" "sudo reboot"
done

echo "All reboot are launched"