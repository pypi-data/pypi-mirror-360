from google.oauth2 import service_account
from google.cloud import compute_v1, redis_v1, storage
from googleapiclient.discovery import build
from typing import Dict, Any, List
from google.protobuf.json_format import MessageToDict



class GCP:
    def __init__(self, tool_config: Dict[str, Any]):
        self.tool_config = tool_config
        self.project_id = tool_config.get("project_id")
        self.region = tool_config.get("region", "asia-south1-a")
        self.credentials = service_account.Credentials.from_service_account_info(tool_config)

        self.compute_client = compute_v1.InstancesClient(credentials=self.credentials)
        self.network_client = compute_v1.NetworksClient(credentials=self.credentials)
        self.subnet_client = compute_v1.SubnetworksClient(credentials=self.credentials)
        self.firewall_client = compute_v1.FirewallsClient(credentials=self.credentials)
        self.redis_client = redis_v1.CloudRedisClient(credentials=self.credentials)
        self.storage_client = storage.Client(credentials=self.credentials, project=self.project_id)
        self.sql_service = build('sqladmin', 'v1beta4', credentials=self.credentials)

    def get_instances(self) -> List[Dict[str, Any]]:
        instances = []
        request = compute_v1.AggregatedListInstancesRequest(project=self.project_id)
        response = self.compute_client.aggregated_list(request=request)

        for zone, instance_list in response:
            if hasattr(instance_list, "instances"):
                for instance in instance_list.instances:
                    instance_dict = {
                        "InstanceId": instance.id,
                        "InstanceName": instance.name,
                        "MachineType": instance.machine_type.split("/")[-1],
                        "Zone": zone,
                        "Status": instance.status,
                        "Tags": list(instance.tags.items) if instance.tags else [],
                        "NetworkInterfaces": [{
                            "Network": nic.network,
                            "Subnetwork": nic.subnetwork,
                            "InternalIP": nic.network_i_p,
                            "ExternalIP": next((cfg.nat_i_p for cfg in nic.access_configs if cfg.nat_i_p), None)
                        } for nic in instance.network_interfaces],
                        "_raw": MessageToDict(instance._pb)  # ✅ SAFE FOR JSON
                    }
                    instances.append(instance_dict)
        return instances


    def get_vpcs(self) -> Dict[str, Any]:
        vpcs = {}
        for network in self.network_client.list(project=self.project_id):
            vpcs[network.id] = {
                "Name": network.name,
                "AutoCreateSubnetworks": network.auto_create_subnetworks
            }
        return vpcs

    def get_subnets(self) -> Dict[str, Any]:
        subnets = {}
        for subnet in self.subnet_client.list(project=self.project_id, region=self.region):
            subnets[subnet.id] = {
                "InstanceName": subnet.name,
                "InstanceId": subnet.network.split("/")[-1],
                "IPRange": subnet.ip_cidr_range,
                "Zone": subnet.region.split("/")[-1],
                "_raw": subnet
            }
        return subnets

    def get_firewall_rules(self) -> Dict[str, Any]:
        rules = {}
        for rule in self.firewall_client.list(project=self.project_id):
            rules[rule.id] = {
                "InstanceName": rule.name,
                "InstanceId": rule.name,
                "Zone": rule.region.split("/")[-1],
                "Direction": rule.direction,
                "Allowed": [{"IPProtocol": a.i_p_protocol, "Ports": a.ports} for a in rule.allowed],
                "SourceRanges": rule.source_ranges,
                "TargetTags": rule.target_tags,
                "_raw": rule
            }
        return rules

    def get_redis_instances(self, location: str = None) -> List[Dict[str, Any]]:
        
        if location:
            parent = f"projects/{self.project_id}/locations/{location}"
        else:
            parent = f"projects/{self.project_id}/locations/{self.region}"
        
        response = self.redis_client.list_instances(request={"parent": parent})
        return [{
            "InstanceName": inst.name.split("/")[-1],
            "InstanceId": inst.name.split("/")[-1],
            "Zone": location,
            "MemorySizeGb": inst.memory_size_gb,
            "Tier": inst.tier.name,
            "Host": inst.host,
            "Port": inst.port,
            "Status": inst.state.name,
            "_raw": MessageToDict(inst._pb)
        } for inst in response.instances]

    def get_storage_buckets(self) -> List[Dict[str, Any]]:
        buckets = self.storage_client.list_buckets()
        return [{
            "InstanceName": bucket.name,
            "InstanceId": bucket.name,
            "Zone": bucket.location,
            "StorageClass": bucket.storage_class,
            "_raw": {
                "name": bucket.name,
                "id": bucket.id,
                "location": bucket.location,
                "storage_class": bucket.storage_class,
                "created": bucket.time_created.isoformat() if bucket.time_created else None,
                "updated": bucket.updated.isoformat() if bucket.updated else None,
                "labels": bucket.labels,
                "self_link": bucket.self_link,
                "etag": bucket.etag,
            }
        } for bucket in buckets]

    def get_sql_instances(self) -> List[Dict[str, Any]]:
        response = self.sql_service.instances().list(project=self.project_id).execute()
        return [{
            "InstanceName": inst["name"],
            "InstanceId": inst["name"],
            "Zone": inst["region"],
            "DatabaseVersion": inst["databaseVersion"],
            "Tier": inst["settings"]["tier"],
            "IpAddresses": inst.get("ipAddresses", []),
            "_raw": inst
        } for inst in response.get("items", [])]
