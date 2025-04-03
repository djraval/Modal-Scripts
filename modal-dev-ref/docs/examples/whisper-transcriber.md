# Parallel podcast transcription using Whisper

This example shows how to build a massively parallel application on Modal: the
Modal Podcast Transcriber.

![homepage of modal whisper transcriber app](/_app/immutable/assets/modal-
podcast-transcriber-frontpage.CDX3OEI-.png)

This example application is more feature-packed than others, and it doesn’t
fit in a single page of code and commentary. So instead of progressing through
the example’s code linearly, this document provides a higher-level walkthrough
of how Modal is used to do fast, on-demand podcast episode transcription for
whichever podcast you’d like.

You can find the code here.

## Hour-long episodes transcribed in just 1 minute

The focal point of this demonstration app is that it does serverless CPU
transcription across dozens of containers at the click of a button, completing
hour-long audio files in just 1 minute.

We use a podcast metadata API to allow users to transcribe an arbitrary
episode from whatever niche podcast they desire — how about _The Pen Addict_ ,
a podcast dedicated to stationery?

The video below shows the 45-minute long first episode of _Serial_ season 2
get transcribed in 62 seconds.

Each transcription segment includes links back to the original audio.

### Try it yourself

If you’re itching to see this in action, here are links to begin transcribing
three popular podcasts:

  1. _Case 63_ by Gimlet Media
  2. _The Joe Rogan Experience_
  3. _The Psychology of your 20s_

## Tech-stack overview

The entire application is hosted serverlessly on Modal and consists of these
main components:

  * A React + Vite single page application (SPA) deployed as static files into a Modal web endpoint.
  * A Python backend running FastAPI in a Modal web endpoint.
  * The Podchaser API provides podcast search and episode metadata retrieval. It’s hooked into our code with a Modal Secret.
  * A Modal async job queue, described in more detail below.

All of this is deployed with one command and costs `$0.00` when it’s not
transcribing podcasts or serving HTTP requests.

### Speed-boosting Whisper with parallelism

Modal’s dead-simple parallelism primitives are the key to doing the
transcription so quickly. Even with a GPU, transcribing a full episode
serially was taking around 10 minutes.

But by pulling in `ffmpeg` with a simple `.pip_install("ffmpeg-python")`
addition to our Modal Image, we could exploit the natural silences of the
podcast medium to partition episodes into hundreds of short segments. Each
segment is transcribed by Whisper in its own container task, and when all are
done we stitch the segments back together with only a minimal loss in
transcription quality. This approach actually accords quite well with
Whisper’s model architecture:

> “The Whisper architecture is a simple end-to-end approach, implemented as an
> encoder-decoder Transformer. Input audio is split into 30-second chunks,
> converted into a log-Mel spectrogram, and then passed into an encoder.”
>
> ― _Introducing Whisper_

## Run this app on Modal

All source code for this example can be found on GitHub. The `README.md`
includes instructions on setting up the frontend build and getting
authenticated with the Podchaser API. Happy transcribing!

