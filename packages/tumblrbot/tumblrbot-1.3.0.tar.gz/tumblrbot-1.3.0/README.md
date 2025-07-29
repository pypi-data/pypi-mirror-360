[OAuth]: https://oauth.net/1
[OpenAI]: https://pypi.org/project/openai
[Python]: https://python.org/download
[Tumblr]: https://tumblr.com

[keyring]: https://pypi.org/project/keyring
[Rich]: https://pypi.org/project/rich

[Moderation API]: https://platform.openai.com/docs/api-reference/moderations
[pip]: https://pypi.org

[Download]: src/tumblrbot/flow/download.py
[Examples]: src/tumblrbot/flow/examples.py
[Fine-Tune]: src/tumblrbot/flow/fine_tune.py
[Generate]: src/tumblrbot/flow/generate.py
[Main]: src/tumblrbot/__main__.py
[README.md]: README.md

[config]: #configuration

# tumblrbot
[![PyPI - Version](https://img.shields.io/pypi/v/tumblrbot)](https://python.org/pypi/tumblrbot)

Description of original project:
> 4tv-tumblrbot was a collaborative project I embarked on with my close friend Dima, who goes by @smoqueen on Tumblr. The aim of this endeavor was straightforward yet silly: to develop a Tumblr bot powered by a machine-learning model. This bot would be specifically trained on the content from a particular Tumblr blog or a selected set of blogs, allowing it to mimic the style, tone, and thematic essence of the original posts.

This fork is largely a rewrite of the source code with similarities in its structure and process.

Features:
- An [interactive console][Main] for all steps of generating posts for the blog:
   1. Asks for [OpenAI] and [Tumblr] tokens.
      - Stores API tokens using [keyring].
      - Prevents API tokens from printing to the console.
   1. Retrieves [Tumblr] [OAuth] tokens.
   1. [Downloads posts][Download] from the [configured][config] [Tumblr] blogs.
      - Skips redownloading already downloaded posts.
      - Shows progress and previews the current post.
   1. [Creates examples][Examples] to fine-tune the model from your posts.
      - Filters out posts that contain more than just text data.
      - Filters out any posts flagged by the [OpenAI] [Moderation API] (optional).
         - Shows progress and previews the current post.
      - Formats asks as the user message and the responses as the assistant response.
      - Adds custom user messages and assistant responses to the dataset from the [configured][config] file.
   1. Provides cost estimates if the currently saved examples are used to fine-tune the [configured][config] model.
   1. [Uploads examples][Fine-Tune] to [OpenAI] and begins the fine-tuning process.
      - Resumes monitoring the same fine-tuning process when restarted.
      - Stores the output model automatically when fine-tuning is completed.
   1. [Generates and uploads posts][Generate] to the [configured][config] [Tumblr] blog using the [configured][config] fine-tuned model.
      - Creates tags by extracting keywords at the [configured][config] frequency using the [configured][config] model.
      - Uploads posts as drafts to the [configured][config] [Tumblr] blog.
      - Shows progress and previews the current post.
- Colorful output, progress bars, and post previews using [rich].
- Automatically keeps the [config] file up-to-date and recreates it if missing.

**To-Do:**
- Add documentation.
- Finish updating [README.md].


**Please submit an issue or contact us for features you want added/reimplemented.**

## Installation
1. Install the latest version of [Python]:
   - Windows: `winget install python3`
   - Linux (apt): `apt install python-pip`
   - Linux (pacman): `pacman install python-pip`
1. Install the [pip] package: `pip install tumblrbot`
   - Alternatively, you can install from this repository: `pip install git+https://github.com/MaidThatPrograms/tumblrbot.git`
   - On Linux, you will have to make a virtual environment.

## Usage
Run `tumblrbot` from anywhere. Run `tumblrbot --help` for command-line options. Every command-line option corresponds to a value from the [config](#configuration).

## Obtaining Tokens
- The [OpenAI] API token can be created [here](https://platform.openai.com/settings/organization/api-keys).
   1. Leave everything at the defaults and set `Project` to `Default Project`.
   1. Press `Create secret key`.
   1. Press `Copy` to copy the API token to your clipboard.
- The [Tumblr] API tokens can be created [here](https://tumblr.com/oauth/apps).
   1. Press `+ Register Application`.
   1. Enter anything for `Application Name` and `Application Description`.
   1. Enter any URL for `Application Website` and `Default callback URL`, like `https://example.com`.
   1. Enter any email address for `Administrative contact email`. It probably doesn't need to be one you have access to.
   1. Press the checkbox next to `I'm not a robot` and complete the CAPTCHA.
   1. Press `Register`.
   1. You now have access to your `consumer key` next to `Oauth Consumer Key`.
   1. Press `Show secret key` to see your `Consumer Secret`.

When running this program, you will be prompted to enter all of these tokens. **The fields are password-protected, so there will be no output to the console.** If something goes wrong while entering the tokens, you can always reset them by running the program again and answering `y` to the relevant prompt.

After inputting the [Tumblr] tokens, you will be given a URL that you need to open in your browser. Press `Allow`, then copy and paste the URL of the page you are redirected to into the console.

## Configuration
All config options can be found in `config.toml` after running the program once. This will be kept up-to-date if there are changes to the config's format in a future update. This also means it may be worthwhile to double-check the config file after an update. Any changes to the config should be in the changelog for a given version.
> WIP: There will be more information about the config options soon.
