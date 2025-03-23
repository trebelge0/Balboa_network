#!/bin/bash

# Check if python script is specified
if [ -z "$1" ]; then
    echo "Usage: $0 <python_program> <IP1>:<param1>,<param2>,... <IP2>:<param1>,<param2>,..."
    exit 1
fi

PYTHON_PROGRAM=$1
shift # Shift args to manage IP's easily

RPIS=("$@")

# Check if at least 1 IP is given
if [ "${#RPIS[@]}" -lt 1 ]; then
    echo "Usage: $0 <python_program> <IP1>:<param1>,<param2>,... <IP2>:<param1>,<param2>,..."
    exit 1
fi

# Username on RPi's
USER="trebelge"

# SSH key to avoid password
SSH_KEY="/home/trebelge/.ssh/id_ed25519"

ID=0  # Automatic ID

for ARGUMENT in "${RPIS[@]}"; do
    # Separate IP from parameters with ':'
    IFS=":" read -r HOST PARAMS <<< "$ARGUMENT"

    # Replace comas with spaces in the parameters
    PARAMS=$(echo $PARAMS | tr ',' ' ')

    echo "Start on $HOST with ID=$ID and parameters: $PARAMS"

    # Kill previous instance of python script if not terminated
    ssh -i $SSH_KEY $USER@$HOST "sudo pkill -f python"

    gnome-terminal --tab -- bash -c "echo 'Connection SSH to $HOST with ID=$ID'; \
    ssh -t -i $SSH_KEY $USER@$HOST 'echo \"Python script launched on $HOST with ID=$ID and parameters: $PARAMS\"; \
    python3 $PYTHON_PROGRAM $ID $PARAMS; exec bash'" &

    ((ID++))
done

echo "All programs are launched in terminal tabs!"
