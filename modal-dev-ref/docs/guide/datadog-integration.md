# Connecting Modal to your Datadog account

You can use the Modal + Datadog Integration to export Modal function logs to
Datadog. You’ll find the Modal Datadog Integration available for install in
the Datadog marketplace.

## What this integration does

This integration allows you to:

  1. Export Modal audit logs in Datadog
  2. Export Modal function logs to Datadog
  3. Export container metrics to Datadog

## Installing the integration

  1. Open the Modal Tile (or the EU tile here) in the Datadog integrations page
  2. Click “Install Integration”
  3. Click Connect Accounts to begin authorization of this integration. You will be redirected to log into Modal, and once logged in, you’ll be redirected to the Datadog authorization page.
  4. Click “Authorize” to complete the integration setup

## Metrics

The Modal Datadog Integration will forward the following metrics to Datadog:

  * `modal.cpu.utilization`
  * `modal.memory.utilization`
  * `modal.gpu.memory.utilization`
  * `modal.gpu.compute.utilization`

These metrics come free of charge and are tagged with `container_id`,
`environment_name`, and `workspace_name`.

## Structured logging

Logs from Modal are sent to Datadog in plaintext without any structured
parsing. This means that if you have custom log formats, you’ll need to set up
a log processing pipeline in Datadog to parse them.

Modal passes log messages in the `.message` field of the log record. To parse
logs, you should operate over this field. Note that the Modal Integration does
set up some basic pipelines. In order for your pipelines to work, ensure that
your pipelines come before Modal’s pipelines in your log settings.

## Cost Savings

The Modal Datadog Integration will forward all logs to Datadog which could be
costly for verbose apps. We recommend using either Log Pipelines or Index
Exclusion Filters to filter logs before they are sent to Datadog.

The Modal Integration tags all logs with the `environment` attribute. The
simplest way to filter logs is to create a pipeline that filters on this
attribute and to isolate verbose apps in a separate environment.

## Uninstalling the integration

Once the integration is uninstalled, all logs will stop being sent to Datadog,
and authorization will be revoked.

  1. Navigate to the Modal metrics settings page and select “Delete Datadog Integration”.
  2. On the Configure tab in the Modal integration tile in Datadog, click Uninstall Integration.
  3. Confirm that you want to uninstall the integration.
  4. Ensure that all API keys associated with this integration have been disabled by searching for the integration name on the API Keys page.

