# Preemption

All Modal Functions are subject to preemption. If a preemption event
interrupts a running Function, Modal will gracefully terminate the Function
and restart it on the same input.

Preemptions are rare, but it is always possible that your Function is
interrupted. Long-running Functions such as model training Functions should
take particular care to tolerate interruptions, as likelihood of interruption
increases with Function run duration.

## Preparing for interruptions

Design your applications to be fault and preemption tolerant. Modal will send
an interrupt signal (`SIGINT`) to your application code when preemption
occurs. In Python applications, this signal is by default propogated as a
`KeyboardInterrupt`, which you can handle in your code to perform cleanup.

Other best practices for handling preemptions include:

  * Divide long-running operations into small tasks or use checkpoints so that you can save your work frequently.
  * Ensure preemptible operations are safely retryable (ie. idempotent).

## Running uninterruptible Functions

We currently don’t have a way for Functions to avoid the possibility of
interruption, but it’s a planned feature. If you require Functions guaranteed
to run without interruption, please reach out!

