#!/bin/bash


# * Master's Thesis *
# Implementation of a robotic swarm platform
# based on the Balboa self-balancing robot
# © 2025 Romain Englebert


# Check if csv file is specified
if [ -z "$1" ]; then
    echo "Usage: $0 <file.csv <IP1>:<param1>,<param2>,... <IP2>:<param1>,<param2>,..."
    exit 1
fi

FILE=$1

shift # Shift args to manage IP's easily

# IPS from args list
RPIS=("$@")

# Check if at least 1 IP is given
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <IP1> <IP2> ... <IPn>"

    echo "Use default IPs"
    RPIS=("raspberrypiZero1" "raspberrypiZero2" "raspberrypiZero3" "raspberrypiZero4" "raspberrypi" "raspberrypi41" "raspberrypi42" "raspberrypi4L")
fi
DEST_DIR="/home/trebelge/OneDrive/Cours UCL/Thesis/Balboa_network/Plots/data"

SSH_KEY="/home/trebelge/.ssh/id_ed25519"

USER="trebelge"

REMOTE_CSV_PATH="/home/trebelge/Documents/Balboa_Network/data/$FILE"

mkdir -p "$DEST_DIR"

ID=0  # Automatic ID

for HOST in "${RPIS[@]}"; do
    echo "📡 Récupération du fichier CSV depuis $HOST (ID=$ID)..."

    scp -i "$SSH_KEY" "$USER@$HOST:$REMOTE_CSV_PATH" "$DEST_DIR/$ID.csv"

    if [ $? -eq 0 ]; then
        echo "✅ Fichier récupéré et enregistré sous $DEST_DIR/$ID.csv"
    else
        echo "❌ Échec du transfert depuis $HOST"
    fi
    ((ID++))
done

echo "🎯 Tous les fichiers ont été récupérés !"
