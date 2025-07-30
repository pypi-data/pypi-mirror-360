from botocore.exceptions import ClientError

from daydream.plugins.aws.arn.arn import AwsArn
from daydream.plugins.aws.nodes.base import AwsNode
from daydream.plugins.aws.utils import swallow_boto_client_access_errors
from daydream.utils import print


class AwsAlbTargetGroup(AwsNode):
    async def get_identifiers(self) -> list[str | None]:
        return [
            *await super().get_identifiers(),
            self.raw_data["TargetGroupArn"],
        ]

    async def get_reference_identifiers(
        self,
    ) -> list[str | None | tuple[str | None, str]]:
        return [
            *await super().get_reference_identifiers(),
            *((lb, "routes_requests_for") for lb in self.raw_data.get("LoadBalancerArns", [])),
            self.raw_data.get("VpcId"),
            *await self._get_targets(),
        ]

    async def _get_targets(self) -> list[tuple[str, str]]:
        try:
            arn = AwsArn.parse(self.node_id)
        except ValueError as ex:
            print(f"Invalid ARN format for target group {self.node_id}: {ex}")
            return []
        async with (
            swallow_boto_client_access_errors(service_name="elbv2", region=arn.region),
            self.session.client("elbv2", region_name=arn.region) as client,
        ):
            try:
                resp = await client.describe_target_health(TargetGroupArn=self.node_id)
            except ClientError as ex:
                print(f"Error describing target health for {self.node_id}: {ex}")
                return []
        # FIXME: find a way to scope this to only searching aws resources (or maybe even ec2 resources) [tvd, 2025-06-27]
        return [
            (target.get("Target", {}).get("Id"), "has_target")
            for target in resp.get("TargetHealthDescriptions", [])
            if target.get("Target", {}).get("Id") is not None
        ]
