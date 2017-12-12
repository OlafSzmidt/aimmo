#!/usr/bin/env bash
set -e
kubectl delete rc aimmo_game_creator || true
sleep 10
kubectl delete rc -l app=aimmo_game
sleep 10
kubectl delete pod -l app=aimmo_game_worker
kubectl delete service -l app=aimmo_game
sleep 5
kubectl create -f rc-aimmo_game_creator.yaml
sleep 10
kubectl get rc
kubectl get pod
kubectl get service
kubectl get ingress
