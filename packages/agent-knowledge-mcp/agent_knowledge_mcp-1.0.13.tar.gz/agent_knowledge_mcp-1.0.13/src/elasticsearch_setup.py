"""
Elasticsearch Docker setup and management.
"""
import json
import subprocess
import time
import requests
from pathlib import Path
from typing import Dict, Any, Optional
import docker
from docker.errors import DockerException, NotFound


class ElasticsearchSetup:
    """Manage Elasticsearch Docker container setup."""
    
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.docker_client = None
        self.container_name = "elasticsearch-mcp"
        self.kibana_container_name = "kibana-mcp"
        
    def _get_docker_client(self):
        """Get Docker client."""
        if self.docker_client is None:
            try:
                self.docker_client = docker.from_env()
                # Test connection
                self.docker_client.ping()
            except DockerException as e:
                raise ConnectionError(f"Cannot connect to Docker. Is Docker running? Error: {e}")
        return self.docker_client
    
    def _is_elasticsearch_running(self, host: str, port: int) -> bool:
        """Check if Elasticsearch is running at the given host:port."""
        try:
            response = requests.get(f"http://{host}:{port}", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _wait_for_elasticsearch(self, host: str, port: int, timeout: int = 60) -> bool:
        """Wait for Elasticsearch to be ready."""
        print(f"Waiting for Elasticsearch at {host}:{port}...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self._is_elasticsearch_running(host, port):
                print("✅ Elasticsearch is ready!")
                return True
            time.sleep(2)
            print("⏳ Still waiting...")
        
        print("❌ Timeout waiting for Elasticsearch")
        return False
    
    def _container_exists(self, container_name: str) -> bool:
        """Check if container exists."""
        try:
            client = self._get_docker_client()
            client.containers.get(container_name)
            return True
        except NotFound:
            return False
    
    def _is_container_running(self, container_name: str) -> bool:
        """Check if container is running."""
        try:
            client = self._get_docker_client()
            container = client.containers.get(container_name)
            return container.status == 'running'
        except NotFound:
            return False
    
    def start_elasticsearch_container(self) -> Dict[str, Any]:
        """Start Elasticsearch container."""
        client = self._get_docker_client()
        
        # Check if container already exists
        if self._container_exists(self.container_name):
            if self._is_container_running(self.container_name):
                print(f"Container {self.container_name} is already running")
                return {"status": "already_running", "host": "localhost", "port": 9200}
            else:
                # Start existing container
                print(f"🔄 Starting existing container {self.container_name}")
                container = client.containers.get(self.container_name)
                container.start()
        else:
            # Create new container
            print(f"🚀 Creating new Elasticsearch container {self.container_name}")
            
            environment = {
                "discovery.type": "single-node",
                "ES_JAVA_OPTS": "-Xms512m -Xmx512m",
                "xpack.security.enabled": "false",
                "xpack.security.enrollment.enabled": "false"
            }
            
            ports = {"9200/tcp": 9200, "9300/tcp": 9300}
            
            container = client.containers.run(
                "docker.elastic.co/elasticsearch/elasticsearch:8.14.1",
                name=self.container_name,
                environment=environment,
                ports=ports,
                detach=True,
                restart_policy={"Name": "unless-stopped"}
            )
            
            print(f"📦 Container {self.container_name} created")
        
        # Wait for Elasticsearch to be ready
        if self._wait_for_elasticsearch("localhost", 9200):
            return {"status": "running", "host": "localhost", "port": 9200}
        else:
            raise RuntimeError("Failed to start Elasticsearch within timeout")
    
    def start_kibana_container(self) -> Dict[str, Any]:
        """Start Kibana container."""
        client = self._get_docker_client()
        
        # Check if Elasticsearch is running first
        if not self._is_container_running(self.container_name):
            raise RuntimeError("Elasticsearch container must be running before starting Kibana")
        
        # Check if Kibana container already exists
        if self._container_exists(self.kibana_container_name):
            if self._is_container_running(self.kibana_container_name):
                print(f"✅ Container {self.kibana_container_name} is already running")
                return {"status": "already_running", "host": "localhost", "port": 5601}
            else:
                # Start existing container
                print(f"🔄 Starting existing container {self.kibana_container_name}")
                container = client.containers.get(self.kibana_container_name)
                container.start()
        else:
            # Create new container
            print(f"🚀 Creating new Kibana container {self.kibana_container_name}")
            
            environment = {
                "ELASTICSEARCH_HOSTS": "http://elasticsearch-mcp:9200"
            }
            
            ports = {"5601/tcp": 5601}
            
            container = client.containers.run(
                "docker.elastic.co/kibana/kibana:8.14.1",
                name=self.kibana_container_name,
                environment=environment,
                ports=ports,
                links={self.container_name: "elasticsearch-mcp"},
                detach=True,
                restart_policy={"Name": "unless-stopped"}
            )
            
            print(f"📦 Container {self.kibana_container_name} created")
        
        # Wait a bit for Kibana to start
        print("⏳ Waiting for Kibana to start...")
        time.sleep(10)
        
        return {"status": "running", "host": "localhost", "port": 5601}
    
    def setup_elasticsearch(self, include_kibana: bool = True) -> Dict[str, Any]:
        """Complete Elasticsearch setup with optional Kibana."""
        print("🔧 Setting up Elasticsearch...")
        
        # Start Elasticsearch
        es_result = self.start_elasticsearch_container()
        
        result = {
            "elasticsearch": es_result,
            "kibana": None
        }
        
        # Start Kibana if requested
        if include_kibana:
            try:
                kibana_result = self.start_kibana_container()
                result["kibana"] = kibana_result
            except Exception as e:
                print(f"⚠️  Warning: Failed to start Kibana: {e}")
                result["kibana"] = {"status": "failed", "error": str(e)}
        
        return result
    
    def update_config(self, host: str, port: int) -> None:
        """Update configuration file with Elasticsearch connection details."""
        try:
            # Load current config
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Update Elasticsearch settings
            config["elasticsearch"]["host"] = host
            config["elasticsearch"]["port"] = port
            config["elasticsearch"]["auto_setup"] = True
            
            # Save updated config
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Updated config file: {host}:{port}")
            
        except Exception as e:
            print(f"❌ Failed to update config: {e}")
            raise
    
    def get_container_status(self) -> Dict[str, Any]:
        """Get status of Elasticsearch and Kibana containers."""
        try:
            client = self._get_docker_client()
            
            status = {
                "elasticsearch": {
                    "exists": self._container_exists(self.container_name),
                    "running": self._is_container_running(self.container_name),
                    "container_name": self.container_name
                },
                "kibana": {
                    "exists": self._container_exists(self.kibana_container_name),
                    "running": self._is_container_running(self.kibana_container_name),
                    "container_name": self.kibana_container_name
                }
            }
            
            return status
            
        except Exception as e:
            return {"error": str(e)}
    
    def stop_containers(self) -> Dict[str, Any]:
        """Stop Elasticsearch and Kibana containers."""
        try:
            client = self._get_docker_client()
            results = {}
            
            # Stop Kibana first
            if self._container_exists(self.kibana_container_name):
                container = client.containers.get(self.kibana_container_name)
                container.stop()
                results["kibana"] = "stopped"
            
            # Stop Elasticsearch
            if self._container_exists(self.container_name):
                container = client.containers.get(self.container_name)
                container.stop()
                results["elasticsearch"] = "stopped"
            
            return results
            
        except Exception as e:
            return {"error": str(e)}


def check_elasticsearch_config(config: Dict[str, Any]) -> bool:
    """Check if Elasticsearch is properly configured and accessible."""
    try:
        host = config["elasticsearch"]["host"]
        port = config["elasticsearch"]["port"]
        
        # Try to connect
        response = requests.get(f"http://{host}:{port}", timeout=5)
        return response.status_code == 200
        
    except:
        return False


def auto_setup_elasticsearch(config_path: Path, config: Dict[str, Any]) -> Dict[str, Any]:
    """Auto-setup Elasticsearch if not configured or not accessible."""
    
    # Check if Elasticsearch is already configured and accessible
    if check_elasticsearch_config(config):
        host = config["elasticsearch"]["host"]
        port = config["elasticsearch"]["port"]
        print(f"Elasticsearch already running at {host}:{port}")
        return {"status": "already_configured", "host": host, "port": port}
    
    print("Elasticsearch not accessible, starting auto-setup...")
    
    # Setup Elasticsearch using Docker
    setup = ElasticsearchSetup(config_path)
    
    try:
        result = setup.setup_elasticsearch(include_kibana=True)
        
        # Update config file
        es_host = result["elasticsearch"]["host"]
        es_port = result["elasticsearch"]["port"]
        setup.update_config(es_host, es_port)
        
        print("🎉 Elasticsearch setup completed!")
        print(f"📍 Elasticsearch: http://{es_host}:{es_port}")
        
        if result["kibana"] and result["kibana"]["status"] in ["running", "already_running"]:
            kibana_host = result["kibana"]["host"]
            kibana_port = result["kibana"]["port"]
            print(f"📊 Kibana: http://{kibana_host}:{kibana_port}")
        
        return {
            "status": "setup_completed",
            "elasticsearch": result["elasticsearch"],
            "kibana": result["kibana"]
        }
        
    except Exception as e:
        print(f"❌ Failed to setup Elasticsearch: {e}")
        return {"status": "setup_failed", "error": str(e)}