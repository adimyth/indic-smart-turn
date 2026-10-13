#!/usr/bin/env python3
"""Create (or find) the training pod on RunPod and print its SSH endpoint.
usage: pod_create.py [--gpu "NVIDIA RTX A6000"] [--stop|--terminate]"""
import argparse, json, os, sys, time, urllib.request
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / ".env")
KEY = os.environ["RUNPOD_API_KEY"]; NAME = "indic-smart-turn"
IMAGE = "runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404"

def gql(query, variables=None):
    req = urllib.request.Request("https://api.runpod.io/graphql", data=json.dumps({"query": query, "variables": variables or {}}).encode(),
                                 headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json", "User-Agent": "curl/8.0"})
    d = json.load(urllib.request.urlopen(req, timeout=60))
    if d.get("errors"): raise SystemExit(f"GraphQL error: {d['errors']}")
    return d["data"]

def find_pod():
    for p in gql("{ myself { pods { id name desiredStatus costPerHr runtime { ports { ip isIpPublic privatePort publicPort type } } machine { gpuDisplayName } } } }")["myself"]["pods"]:
        if p["name"] == NAME: return p
    return None

def create(gpu, volume_gb, disk_gb):
    q = """mutation($in: PodFindAndDeployOnDemandInput!) { podFindAndDeployOnDemand(input: $in) { id costPerHr machine { gpuDisplayName } } }"""
    inp = {"cloudType": "ALL", "gpuCount": 1, "gpuTypeId": gpu, "name": NAME, "imageName": IMAGE,
           "volumeInGb": volume_gb, "containerDiskInGb": disk_gb, "volumeMountPath": "/workspace",
           "minVcpuCount": 8, "minMemoryInGb": 32, "ports": "22/tcp", "startSsh": True, "dockerArgs": "",
           "env": [{"key": "HF_TOKEN", "value": os.environ["HF_TOKEN"]}, {"key": "HF_HOME", "value": "/workspace/hf"}]}
    return gql(q, {"in": inp})["podFindAndDeployOnDemand"]

def ssh_endpoint(pod):
    for port in (pod.get("runtime") or {}).get("ports") or []:
        if port["privatePort"] == 22 and port["isIpPublic"]:
            return port["ip"], port["publicPort"]
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gpu", default="NVIDIA RTX A6000")
    ap.add_argument("--fallback", nargs="*", default=["NVIDIA A40", "NVIDIA GeForce RTX 4090", "NVIDIA L40"])
    ap.add_argument("--volume-gb", type=int, default=150); ap.add_argument("--disk-gb", type=int, default=40)
    ap.add_argument("--stop", action="store_true"); ap.add_argument("--terminate", action="store_true")
    a = ap.parse_args()
    pod = find_pod()
    if a.stop or a.terminate:
        if not pod: print("no pod"); return
        gql("mutation($id:String!){ podStop(input:{podId:$id}) { id } }" if a.stop else "mutation($id:String!){ podTerminate(input:{podId:$id}) }", {"id": pod["id"]})
        print("stopped" if a.stop else "terminated", pod["id"]); return
    if pod and pod["desiredStatus"] == "EXITED":
        gql("mutation($id:String!){ podResume(input:{podId:$id, gpuCount:1}) { id } }", {"id": pod["id"]}); print("resuming", pod["id"])
    if not pod:
        for gpu in [a.gpu] + a.fallback:
            try:
                r = create(gpu, a.volume_gb, a.disk_gb); print(f"created pod {r['id']} on {r['machine']['gpuDisplayName']} at ${r['costPerHr']}/h"); break
            except SystemExit as e:
                print(f"{gpu}: {e}")
        else:
            sys.exit("no GPU available")
    for _ in range(60):
        pod = find_pod(); ep = ssh_endpoint(pod) if pod else None
        if ep:
            print(f"SSH_HOST={ep[0]}\nSSH_PORT={ep[1]}\nssh -o StrictHostKeyChecking=no -p {ep[1]} root@{ep[0]}")
            Path(".pod_ssh").write_text(f"{ep[0]} {ep[1]}\n"); return
        time.sleep(10)
    sys.exit("pod did not expose ssh in time")

if __name__ == "__main__":
    main()
