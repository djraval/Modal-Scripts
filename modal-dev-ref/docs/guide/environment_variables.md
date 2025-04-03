# Environment variables

## Runtime environment variables

The Modal runtime sets several environment variables during initialization.
The keys for these environment variables are reserved and cannot be overridden
by your Function configuration.

The following variables provide information about the function’s runtime
environment:

  * **`MODAL_CLOUD_PROVIDER`** — Modal executes functions across a number of cloud providers (AWS, GCP, OCI). This variable specifies which cloud provider the Modal Function is running within.
  * **`MODAL_ENVIRONMENT`** — The name of the Modal Environment the function is running within.
  * **`MODAL_IMAGE_ID`** — The ID of the `modal.Image` used by the Modal Function.
  * **`MODAL_IS_REMOTE`** \- Set to ‘1’ to indicate that the function code is running in a remote container.
  * **`MODAL_REGION`** — This will correspond to a geographic area identifier from the cloud provider associated with the Function (see above). For AWS, the identifier is a “region”. For GCP it is a “zone”, and for OCI it is an “availability domain”. Example values are `us-east-1` (AWS), `us-central1` (GCP), `us-ashburn-1` (OCI).
  * **`MODAL_TASK_ID`** — The ID of the container running the Modal Function.
  * **`MODAL_IDENTITY_TOKEN`** — An OIDC token encoding the identity of the Modal Function.

## Container image environment variables

The container image layers used by a Modal Function’s `modal.Image` may set
environment variables. These variables will be present within your Function’s
runtime environment. For example, the `debian_slim` image sets the `GPG_KEY`
variable.

To override image variables or set new ones, use the `.env` method provided by
`modal.Image`.

