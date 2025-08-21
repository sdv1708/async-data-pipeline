# Root module stitching together all infrastructure components.
# Individual services are defined in their respective *.tf files
# (networking.tf, msk.tf, ecs.tf, rds.tf, redis.tf, observability.tf, budgets.tf).
# Terraform automatically combines these files into a single configuration.
