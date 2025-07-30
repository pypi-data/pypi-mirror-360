# Live Text Bridge from Presentation

This tool retrieves text from the current presentation on Microsoft PowerPoint or LibreOffice Impress,
modifies the text, and send it to your live streaming.

This tool bridges from presentation texts to streaming lower-thirds during live event.
While a presentation slideshow is being displayed in-person,
this tool retrieves the current slide's text,
optionally applies small modifications,
and sends it to OBS Studio *Text Source* or vMix *Browser Input*.
-- typically as a lower-third overlay during a livestream.

## Features

- Captures live slideshow from these tools
  - Microsoft PowerPoint
  - LibreOffice Impress
- Filters
  - Selects shapes by placeholder, size, etc. powered by [JMESPath](https://jmespath.org/).
  - Line break adjustment.
  - Text replacement with regular expression.
- Sends to:
  - OBS Studio (via [obs-websocket](https://github.com/obsproject/obs-websocket))
  - Web browser in real time (via built-in webserver, for vMix or browser overlays)

## Use Case

This tool is ideal for:
- Church services, seminars, or other events where PowerPoint is used for the in-person audience.
- Situations where text overlays need to match slide content automatically without manual edits.

## Requirements

- Host running presentation tool
  - Microsoft Windows + PowerPoint (desktop version)
  - Linux + LibreOffice Impress
- Host running the streaming
  - OBS Studio 30 or later

(In future, we might support more tools.)

## Configuration

Edit `config.yaml` to set these information.
- Shape selection rule
- Text format rules
- For OBS websocket; URL, password, and target text source name
- For browser (such as vMix); configure the `webserver` output to enable browser-based overlays.

Note: If presentation and streaming run on the different computers,
run this program on the computer running PowerPoint or Impress.

## Usage

- Start your presentation slideshow as usual.
- Run `slidetextbridge.exe`
  The program will show up a console window. You can minimize it.
- Also run OBS Studio.

Footnote: You may start this tool either earlier or later than starting the presentation tool.

## Example Config

### For OBS Studio

```yaml
steps:
  - type: ppt
  - type: obsws
    url: ws://localhost:4455/
    password:
    source_name: 'Text (GDI+)'
```

### For Web Browser Output

```yaml
steps:
  - type: ppt
  - type: webserver
    host: 0.0.0.0
    port: 8080
```

Open `http://127.0.0.1:8080/` (or use your computer's IP address) on your browser.

## Learn More

- [Getting Started](https://norihiro.github.io/slidetextbridge/doc/getting-started.html)
- [Gallery](https://github.com/norihiro/slidetextbridge/wiki/Gallery)
