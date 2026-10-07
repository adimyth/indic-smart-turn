#!/usr/bin/env bash
# run a command on the pod: pod_ssh.sh "cmd"
cd "$(dirname "$0")/.."; read HOST PORT < .pod_ssh
ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -p "$PORT" root@"$HOST" "$@"
