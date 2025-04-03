# Cloud bucket mounts

The `modal.CloudBucketMount` is a mutable volume that allows for both reading
and writing files from a cloud bucket. It supports AWS S3, Cloudflare R2, and
Google Cloud Storage buckets.

Cloud bucket mounts are built on top of AWS’ `mountpoint` technology and
inherits its limitations. Notably, mode changes are disabled, so commands like
`chmod` and `shutil.copymode()` will fail.

## Mounting Cloudflare R2 buckets

`CloudBucketMount` enables Cloudflare R2 buckets to be mounted as file system
volumes. Because Cloudflare R2 is S3-Compatible the setup is very similar
between R2 and S3. See modal.CloudBucketMount for usage instructions.

When creating the R2 API token for use with the mount, you need to have the
ability to read, write, and list objects in the specific buckets you will
mount. You do _not_ need admin permissions, and you should _not_ use “Client
IP Address Filtering”.

## Mounting Google Cloud Storage buckets

`CloudBucketMount` enables Google Cloud Storage (GCS) buckets to be mounted as
file system volumes. See modal.CloudBucketMount for GCS setup instructions.

## Mounting S3 buckets

`CloudBucketMount` enables S3 buckets to be mounted as file system volumes. To
interact with a bucket, you must have the appropriate IAM permissions
configured (refer to the section on IAM Permissions).

    
    
    import modal
    import subprocess
    
    app = modal.App()
    
    s3_bucket_name = "s3-bucket-name"  # Bucket name not ARN.
    s3_access_credentials = modal.Secret.from_dict({
        "AWS_ACCESS_KEY_ID": "...",
        "AWS_SECRET_ACCESS_KEY": "...",
        "AWS_REGION": "..."
    })
    
    @app.function(
        volumes={
            "/my-mount": modal.CloudBucketMount(s3_bucket_name, secret=s3_access_credentials)
        }
    )
    def f():
        subprocess.run(["ls", "/my-mount"])

Copy

### Specifying S3 bucket region

Amazon S3 buckets are associated with a single AWS Region. `Mountpoint`
attempts to automatically detect the region for your S3 bucket at startup time
and directs all S3 requests to that region. However, in certain scenarios,
like if your container is running on an AWS worker in a certain region, while
your bucket is in a different region, this automatic detection may fail.

To avoid this issue, you can specify the region of your S3 bucket by adding an
`AWS_REGION` key to your Modal secrets, as in the code example above.

### Using AWS temporary security credentials

`CloudBucketMount`s also support AWS temporary security credentials by passing
the additional environment variable `AWS_SESSION_TOKEN`. Temporary credentials
will expire and will not get renewed automatically. You will need to update
the corresponding Modal Secret in order to prevent failures.

You can get temporary credentials with the AWS CLI with:

    
    
    $ aws configure export-credentials --format env
    export AWS_ACCESS_KEY_ID=XXX
    export AWS_SECRET_ACCESS_KEY=XXX
    export AWS_SESSION_TOKEN=XXX...

Copy

All these values are required.

### Using OIDC identity tokens

Modal provides OIDC integration and will automatically generate identity
tokens to authenticate to AWS. OIDC eliminates the need for manual token
passing through Modal secrets and is based on short-lived tokens, which limits
the window of exposure if a token is compromised. To use this feature, you
must configure AWS to trust Modal’s OIDC provider and create an IAM role that
can be assumed by Modal Functions.

Then, you specify the IAM role that your Modal Function should assume to
access the S3 bucket.

    
    
    import modal
    
    app = modal.App()
    
    s3_bucket_name = "s3-bucket-name"
    role_arn = "arn:aws:iam::123456789abcd:role/s3mount-role"
    
    @app.function(
        volumes={
            "/my-mount": modal.CloudBucketMount(
                bucket_name=s3_bucket_name,
                oidc_auth_role_arn=role_arn
            )
        }
    )
    def f():
        subprocess.run(["ls", "/my-mount"])

Copy

### Mounting a path within a bucket

To mount only the files under a specific subdirectory, you can specify a path
prefix using `key_prefix`. Since this prefix specifies a directory, it must
end in a `/`. The entire bucket is mounted when no prefix is supplied.

    
    
    import modal
    import subprocess
    
    app = modal.App()
    
    s3_bucket_name = "s3-bucket-name"
    prefix = 'path/to/dir/'
    
    s3_access_credentials = modal.Secret.from_dict({
        "AWS_ACCESS_KEY_ID": "...",
        "AWS_SECRET_ACCESS_KEY": "...",
    })
    
    @app.function(
        volumes={
            "/my-mount": modal.CloudBucketMount(
                bucket_name=s3_bucket_name,
                key_prefix=prefix,
                secret=s3_access_credentials
            )
        }
    )
    def f():
        subprocess.run(["ls", "/my-mount"])

Copy

This will only mount the files in the bucket `s3-bucket-name` that are
prefixed by `path/to/dir/`.

### Read-only mode

To mount a bucket in read-only mode, set `read_only=True` as an argument.

    
    
    import modal
    import subprocess
    
    app = modal.App()
    
    s3_bucket_name = "s3-bucket-name"  # Bucket name not ARN.
    s3_access_credentials = modal.Secret.from_dict({
        "AWS_ACCESS_KEY_ID": "...",
        "AWS_SECRET_ACCESS_KEY": "...",
    })
    
    @app.function(
        volumes={
            "/my-mount": modal.CloudBucketMount(s3_bucket_name, secret=s3_access_credentials, read_only=True)
        }
    )
    def f():
        subprocess.run(["ls", "/my-mount"])

Copy

While S3 mounts supports both write and read operations, they are optimized
for reading large files sequentially. Certain file operations, such as
renaming files, are not supported. For a comprehensive list of supported
operations, consult the Mountpoint documentation.

### IAM permissions

To utilize `CloudBucketMount` for reading and writing files from S3 buckets,
your IAM policy must include permissions for `s3:PutObject`,
`s3:AbortMultipartUpload`, and `s3:DeleteObject`. These permissions are not
required for mounts configured with `read_only=True`.

    
    
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Sid": "ModalListBucketAccess",
          "Effect": "Allow",
          "Action": ["s3:ListBucket"],
          "Resource": ["arn:aws:s3:::<MY-S3-BUCKET>"]
        },
        {
          "Sid": "ModalBucketAccess",
          "Effect": "Allow",
          "Action": [
            "s3:GetObject",
            "s3:PutObject",
            "s3:AbortMultipartUpload",
            "s3:DeleteObject"
          ],
          "Resource": ["arn:aws:s3:::<MY-S3-BUCKET>/*"]
        }
      ]
    }

Copy

