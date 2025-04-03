# Connecting Modal to your Vercel account

You can use the Modal + Vercel integration to access Modal’s Instant Endpoints
from Vercel projects. You’ll find the Modal Vercel integration available for
install in the Vercel AI marketplace.

## What this integration does

This integration allows you to:

  1. Easily synchronize your Modal API keys to one or more Vercel projects
  2. Call Modal’s Instant Endpoints over HTTP in connected Vercel projects

### Authentication

The integration will set the following environment variables against the
user’s selected Vercel projects:

  * `MODAL_TOKEN_ID` (starts with `ak-*`)
  * `MODAL_TOKEN_SECRET` (starts with `as-*`)

The environment variables will be set in the “preview” and “production”
project targets. You can read more about environment variables within Vercel
in the documentation.

## Installing the integration

  1. Click “Add integration” on the Vercel integrations page
  2. Select the Vercel account you want to connect with
  3. (If logged out) Sign into an existing Modal workspace, or create a new Modal workspace
  4. Select the Vercel projects that you wish to connect to your Modal workspace
  5. Click “Continue”
  6. Back in your Vercel dashboard, confirm the environment variables were added by going to your Vercel `project > "Settings" > "Environment variables"`

## Uninstalling the integration

The Modal Vercel integration is managed under the user’s Vercel dashboard
under the “Integrations” tab. From there they can remove the specific
integration installation from their Vercel account.

**Important:** removing an integration will delete the corresponding API token
set by Modal in your Vercel project(s).

* * *

## Modal Instant Endpoints

_Instant Endpoints_ are a fast and scalable API for integrating open-source AI
models into your Vercel app.

All available endpoints are listed below, along with example code suitable for
use with the Javascript `fetch` API.

### Stable Diffusion XL

> https://modal-labs—instant-stable-diffusion-xl.modal.run

Stable Diffusion is a latent text-to-image diffusion model able to generate
photo-realistic images given any text prompt.

This endpoint uses a fast version of Stable Diffusion XL to create variably
sized images up to 1024h x 1024w.

#### Example code

    
    
    // pages/api/modal.ts
    const requestData = {
      prompt: "need for speed supercar. unreal engine",
      width: 768,
      height: 768,
      num_outputs: 1,
    };
    const result = await fetch(
      "https://modal-labs--instant-stable-diffusion-xl.modal.run/v1/inference",
      {
        headers: {
          Authorization: `Token ${process.env.MODAL_TOKEN_ID}:${process.env.MODAL_TOKEN_SECRET}`,
          "Content-Type": "application/json",
        },
        method: "POST",
        body: JSON.stringify(requestData),
      },
    );
    const imageData = await result.blob();

Copy

#### Input schema

  * **prompt`string`**
    * Input prompt
  * **height`integer`**
    * Height of generated image in pixels. Needs to be a multiple of 64
    * One of: `64, 128, 192, 256, 320, 384, 448, 512, 576, 640, 704, 768, 832, 896, 960, 1024`
    * Default: `768`
  * **width`integer`**
    * Width of generated image in pixels. Needs to be a multiple of 64
    * One of: `64, 128, 192, 256, 320, 384, 448, 512, 576, 640, 704, 768, 832, 896, 960, 1024`
    * Default: `768`

#### Output schema

This endpoint outputs `bytes` for a single image with media type
`"image/png"`.

#### Pricing

Requests to this endpoint use duration based pricing, billed at 1ms
granularity. The exact cost per millisecond is based on the underlying GPU
hardware. This endpoint use a single NVIDIA A10G device to serve each request.

See our pricing page for current GPU prices.

Inferences usually complete within 15-30 seconds.

### Transcribe speech with vaibhavs10/insanely-fast-whisper

This endpoint hosts vaibhavs10/insanely-fast-whisper to transcribe and diarize
audio.

#### Example code

    
    
    // pages/api/modal.ts
    const data = {
      audio: dataUrl,
      diarize_audio: false,
    };
    
    const response = await fetch("https://modal-labs--instant-whisper.modal.run", {
      headers: {
        Authorization: `Token ${process.env.MODAL_TOKEN_ID}:${process.env.MODAL_TOKEN_SECRET}`,
      },
      method: "POST",
      body: JSON.stringify(requestData),
    });
    
    const output = await response.json();

Copy

#### Input schema

  * **audio`string`**
    * Input audio file as a Data URL.
  * **language`string`**
    * Language of the input text. Whisper auto-detects the language if not provided. See the full list of options here
    * Default: “
  * **diarize_audio`Boolean`**
    * Whether to diarize the audio.
    * Default: `false`
  * **batch_size`integer`**
    * Number of parallel batches.
    * Default: `24`

#### Output schema

This endpoint outputs a JSON with two fields:

  * **text`string`**
  * **chunks`Chunk[]`**

Here, `Chunk` is a JSON object with the following fields:

  * **speaker`string`**
    * [Optional] only present if `diarize_audio` is `true`
  * **text`string`**
  * **timestamp`[float, float]`**

### Stream text-to-speech with coqui-ai/TTS

XTTS v2 is a fast and high-quality text-to-speech model.

This endpoint uses a streaming version of coqui-ai/TTS that streams wav audio
back as it’s generated in real-time.

#### Example code

    
    
    // pages/api/modal.ts
    const requestData = {
      text: "It is a mistake to think you can solve any major problems just with potatoes.",
      language: "en",
    };
    const result = await fetch("https://modal-labs--instant-xtts-v2.modal.run", {
      headers: {
        Authorization: `Token ${process.env.MODAL_TOKEN_ID}:${process.env.MODAL_TOKEN_SECRET}`,
        "Content-Type": "application/json",
      },
      method: "POST",
      body: JSON.stringify(requestData),
    });
    const audioBuffer = await response.buffer();

Copy

#### Input schema

  * **text`string`**
    * Input text
  * **language`string`**
    * Language of the input text
    * One of: `en, es, fr, de, it, pt, pl, tr, ru, nl, cs, ar, zh, hu, ko, hi`
    * Default: `en`

#### Output schema

This endpoint streams `bytes` for a single audio file with media type
`"audio/wav"`.

### Want more?

If a popular open-source AI model API is not listed here, you can either
implement it in Python and host it on Modal or ask us in Slack to add it as an
Instant Endpoint!

