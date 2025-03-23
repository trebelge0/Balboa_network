#!/bin/bash

# IPS from args list
RPIS=("$@")

# Check if at least 1 IP is given
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <IP1> <IP2> ... <IPn>"

    echo "Use default IPs"
    RPIS=("raspberrypi" "raspberrypi4L" "raspberrypiZero1" "raspberrypiZero2" "raspberrypiZero3" "raspberrypiZero4")
fi
# Dossier de destination sur ton PC
DEST_DIR="/home/trebelge/OneDrive/Cours UCL/Thesis/Balboa_Network/Plots/data"

# Clé SSH
SSH_KEY="/home/trebelge/.ssh/id_ed25519"

# Nom d'utilisateur sur les RPi
USER="trebelge"

# Chemin du fichier CSV sur chaque RPi
REMOTE_CSV_PATH="/home/trebelge/Documents/Balboa_Network/data/consensus.csv"

# Créer le dossier de destination s'il n'existe pas
mkdir -p "$DEST_DIR"

ID=0  # Automatic ID

# Récupérer les fichiers CSV de chaque RPi
for HOST in "${RPIS[@]}"; do
    echo "📡 Récupération du fichier CSV depuis $HOST (ID=$ID)..."

    # Copier le fichier du RPi vers ton PC avec un nouveau nom
    scp -i "$SSH_KEY" "$USER@$HOST:$REMOTE_CSV_PATH" "$DEST_DIR/$ID.csv"

    if [ $? -eq 0 ]; then
        echo "✅ Fichier récupéré et enregistré sous $DEST_DIR/$ID.csv"
    else
        echo "❌ Échec du transfert depuis $HOST"
    fi
    ((ID++))
done

echo "🎯 Tous les fichiers ont été récupérés !"
