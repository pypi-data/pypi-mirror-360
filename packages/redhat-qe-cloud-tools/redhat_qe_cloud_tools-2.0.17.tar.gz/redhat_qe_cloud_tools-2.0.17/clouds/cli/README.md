# Cloud nuke CLI tools
* To run with `cloud-cli`:

```bash
pipx install redhat-qe-cloud-tools
cloud-cli --help
```


### AWS nuke
#### Pre-requisites:
- Install `cloud-nuke` CLI tool (see https://github.com/gruntwork-io/cloud-nuke)

#### Run nuke for specific AWS regions cloud resources:
* Using Poetry:

```bash
poetry run python clouds/cli/cli.py aws-nuke --aws-regions "us-east-1,us-west-2"
```

* Using `cloud-cli`:

```bash
cloud-cli aws-nuke --aws-regions "us-east-1,us-west-2"
```


#### Run nuke for all AWS regions:
* Using Poetry:

```bash
poetry run python clouds/cli/cli.py aws-nuke --all-aws-regions
```

* Using `cloud-cli`:

```bash
cloud-cli aws-nuke --all-aws-regions
```


### Microsoft Azure nuke
#### Run nuke for all Microsoft Azure cloud resources that are associated with given credentials
* Using Poetry:

```bash
poetry run python clouds/cli/cli.py azure-nuke \
                         --azure-tenant-id $AZURE_TENANT_ID \
                         --azure-client-id $AZURE_CLIENT_ID \
                         --azure-client-secret $AZURE_CLIENT_SECRET \
                         --azure-subscription-id $AZURE_SUBSCRIPTION_ID
```

* Using `cloud-cli`:

```bash
cloud-cli azure-nuke \
         --azure-tenant-id $AZURE_TENANT_ID \
         --azure-client-id $AZURE_CLIENT_ID \
         --azure-client-secret $AZURE_CLIENT_SECRET \
         --azure-subscription-id $AZURE_SUBSCRIPTION_ID
```
