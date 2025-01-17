
# Launch New VPC Stack

The `cdk.json` file tells the CDK Toolkit how to execute your app.

You can configure custom parameters in `cdk.json` as well...

For example:

    "vpcCidr": "10.10.0.0/16",
    "vpcId": "CDK VPC",
    "maxAzs": "3",
    "numNatGateways": "0",
    "publicCidrMask": "24",
    "privateCidrMask": "24",
    "mapPublicIp": true,
    "createInternetGateway": true,
    "dnsHostnames": true,
    "dnsSupport": true


To manually create a virtualenv on MacOS and Linux:

```
$ python -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

