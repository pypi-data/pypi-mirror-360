#!/usr/bin/env python

import argparse
from runner import Runner

def main():
    """
    Command-line interface entry point for OBS Switch Controller
    """
    parser = argparse.ArgumentParser(description="OBS and Switch Controller Runner")
    parser.add_argument("--obs-host", default="localhost", help="OBS WebSocket host")
    parser.add_argument("--obs-port", type=int, default=4455, help="OBS WebSocket port")
    parser.add_argument("--obs-password", help="OBS WebSocket password")
    parser.add_argument("--switch-url", default="http://192.168.1.29:8000", help="NXBT webapp URL")
    parser.add_argument("--kafka-bootstrap-servers", default="localhost:9092", help="Kafka bootstrap servers")
    parser.add_argument("--kafka-topics", nargs="+", default=["spl_replay_service"], help="Kafka topics to subscribe to")
    
    args = parser.parse_args()
    
    # Create and run the runner
    runner = Runner()
    runner.run(
        obs_host=args.obs_host,
        obs_port=args.obs_port,
        obs_password=args.obs_password,
        switch_url=args.switch_url,
        kafka_bootstrap_servers=args.kafka_bootstrap_servers,
        kafka_topics=args.kafka_topics
    )

if __name__ == "__main__":
    main()