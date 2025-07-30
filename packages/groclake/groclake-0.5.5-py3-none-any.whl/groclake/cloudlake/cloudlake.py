from ..utillake import Utillake
from ..config import GUPSHUP_URL
import requests
import boto3
import os

class Cloudlake:
    def __init__(self):
        self.utillake = Utillake()
        self.commlake_id = None
        self.params = {}
        self.session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "ap-south-1")
        )
        self.client = self.session.client('cloudtrail')
        self.event_sources = [
            "ec2.amazonaws.com",
            "rds.amazonaws.com",
            "elasticache.amazonaws.com"
        ]
        self.ec2 = self.session.client("ec2")
        self.rds = self.session.client('rds')
        self.elasticache = self.session.client('elasticache')



    def get_region(self):
        return self.ec2.meta.region_name

    def get_vpcs(self):
        vpcs = {}
        response = self.ec2.describe_vpcs()
        for vpc in response["Vpcs"]:
            vpcs[vpc["VpcId"]] = {
                "Name": next((tag["Value"] for tag in vpc.get("Tags", []) if tag["Key"] == "Name"), "N/A")
            }
        return vpcs

    def get_subnets(self):
        subnets = {}
        response = self.ec2.describe_subnets()
        for subnet in response["Subnets"]:
            subnets[subnet["SubnetId"]] = {
                "VpcId": subnet["VpcId"]
            }
        return subnets

    def get_security_groups(self):
        sg_map = {}
        response = self.ec2.describe_security_groups()
        for sg in response["SecurityGroups"]:
            inbound = {}
            for perm in sg["IpPermissions"]:
                from_port = perm.get("FromPort")
                to_port = perm.get("ToPort")
                port_range = f"{from_port}-{to_port}" if from_port is not None else "ALL"
                cidrs = [ip["CidrIp"] for ip in perm.get("IpRanges", [])]
                inbound[port_range] = cidrs
            sg_map[sg["GroupId"]] = {
                "Name": sg.get("GroupName", "N/A"),
                "VpcId": sg.get("VpcId", "N/A"),
                "InboundRules": inbound
            }
        return sg_map

    def get_ec2_instances(self):
        instances = []
        response = self.ec2.describe_instances()

        for res in response["Reservations"]:
            for inst in res["Instances"]:
                instances.append({
                    "InstanceId": inst["InstanceId"],
                    "InstanceType": inst["InstanceType"],
                    "InstanceName": next((tag["Value"] for tag in inst.get("Tags", []) if tag["Key"] == "Name"), "N/A"),
                    "LaunchTime": inst["LaunchTime"],
                    "KeyName": inst.get("KeyName", "N/A"),
                    "PrivateIpAddress": inst.get("PrivateIpAddress", "N/A"),
                    "VpcId": inst.get("VpcId", "N/A"),
                    "SubnetId": inst.get("SubnetId", "N/A"),
                    "SecurityGroups": [sg["GroupId"] for sg in inst.get("SecurityGroups", [])],
                    "VolumeIds": [bdm["Ebs"]["VolumeId"] for bdm in inst.get("BlockDeviceMappings", []) if
                                  "Ebs" in bdm],
                    "Tags": [{tag["Key"]: tag["Value"]} for tag in inst.get("Tags", [])]
                })
        return instances

    def get_rds_instances(self):
        response = self.rds.describe_db_instances()
        return response["DBInstances"]

    def get_elasticache_nodes(self):
        response = self.elasticache.describe_cache_clusters(ShowCacheNodeInfo=True)
        return response["CacheClusters"]

    def modify_security_group_inbound(self, action_data):
        """
        Expected action_data format:
        {
            "description": "teams-ip-white-list",
            "rule_description": "adam",
            "cidr": "110.332.32.25/32"
        }
        """
        description = action_data.get("description")
        rule_description = action_data.get("rule_description")
        new_cidr = action_data.get("cidr")

        if not all([description, rule_description, new_cidr]):
            raise ValueError("Missing required action data fields")

        # Step 1: Find security group ID by description
        response = self.ec2.describe_security_groups()
        security_group_id = None
        for sg in response['SecurityGroups']:
            if sg.get("Description") == description:
                security_group_id = sg["GroupId"]
                break

        if not security_group_id:
            raise Exception("Security group with the given description not found.")

        # Step 2: Get current inbound rules of the security group
        response = self.ec2.describe_security_groups(GroupIds=[security_group_id])
        sg = response['SecurityGroups'][0]
        rule_found = False

        for permission in sg['IpPermissions']:
            for ip_range in permission.get('IpRanges', []):
                if ip_range.get('Description') == rule_description:
                    rule_found = True

                    # Step 3: Revoke the old rule
                    self.ec2.revoke_security_group_ingress(
                        GroupId=security_group_id,
                        IpPermissions=[{
                            'IpProtocol': permission['IpProtocol'],
                            'FromPort': permission.get('FromPort'),
                            'ToPort': permission.get('ToPort'),
                            'IpRanges': [ip_range]
                        }]
                    )
                    # Step 4: Add new rule with updated CIDR
                    self.ec2.authorize_security_group_ingress(
                        GroupId=security_group_id,
                        IpPermissions=[{
                            'IpProtocol': permission['IpProtocol'],
                            'FromPort': permission.get('FromPort'),
                            'ToPort': permission.get('ToPort'),
                            'IpRanges': [{
                                'CidrIp': new_cidr,
                                'Description': rule_description
                            }]
                        }]
                    )
                    return {
                        "SecurityGroupId": security_group_id,
                        "Action": "Rule updated",
                        "OldCIDR": ip_range['CidrIp'],
                        "NewCIDR": new_cidr,
                        "Description": rule_description
                    }

        if not rule_found:
            raise Exception(f"No rule found with description '{rule_description}' in the security group.")
