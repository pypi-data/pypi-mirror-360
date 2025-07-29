# gemspeak
***Gemspeak* is a library that simplifies the `google.genai` library into a simple, easy interface, and provides functions to use multiple API keys at once.**

This chart shows some of the supported features, features in progress, and features that are not currently supported. Check here for updates; "Not Supported" might change eventually!
|Gemini Feature|Support|
|--------|---------|
|Text Generation|✅Supported|
|Image Generation|✅Supported|
|Single-Speaker TTS|✅Supported|
|Multi-Speaker TTS|✅Supported|
|Thinking|✅Supported|
|Inline Content Upload|✅Supported|
|Files API Upload|✅Supported|
|URL Context|✅Supported|
|Code Execution|✅Supported|
|Content Embedding|✅Supported|
|Grounding|✅Supported|
|Content Stream|🟨In Progress|
|Function Calling|🟨In Progress|
|Structured Output|🟨In Progress|
|Music Generation|🟥Not Supported|
|Video Generation|🟥Not Supported|

# Installation

Install via pip with a simple `pip install` command:
```bash
pip install gemspeak
```

# Documentation

## Adding API Keys
The *gemspeak* API supports multiple API keys. When you make a request, *gemspeak* will search through it's list of keys and find one with free prompts remaining.
To add API keys, use the code below:
```
>>> from gemspeak import add_api_keys
>>> add_api_keys(["KEY1", "KEY2", "KEY3"])
```
The API keys are stored in a folder named `gemspeak` in your local appdata file. For example, on Windows this is: `C:\users\username\appdata\local\gemspeak`
## Client
`gemspeak.GemSpeakClient` is a client class which is the main body of the *gemspeak* function and includes most of the usage functions. First, initialize the client:
```
>>> from gemspeak import GemSpeakClient
>>> cli = GemSpeakClient()
```
# Generating Text
Generate text with the client by using the general-purpose `GemSpeakClient.ask_gemini` method. 
Here is a simple example:
```
>>> response = cli.ask_gemini(
...		model="gemini-2.0-flash",
...		text="Hey Gemini, what can you do?"
...)
>>> print(response.text)
*prints text response*
```
# Changing Safety Settings
To change safety settings, use `gemspeak.settings.SafetySettings`
Set each of the safety settings categories with the strings `"BLOCK NONE"`, `"BLOCK FEW"`, `"BLOCK MORE"`, `"BLOCK MOST"`. Set any of the categories with these settings.
Below is an example of how to set safety settings. The section below shows how to use safety settings.
```
>>> from gemspeak import SafetySettings
>>> safety_settings = SafetySettings(
...		harrassment=BLOCK_FEW,
... 	dangerous_content=BLOCK_MOST,
... 	civic_integrity=BLOCK_MORE
... )
```
# Changing Model Settings
To change settings, such as enabling code execution, thinking, or creating image and audio, and changing safety settings, import the following classes: `TextGenSettings`, `ImageGenSettings`, `SingleSpeakerTTSSettings`, `MultiSpeakerTTSSettings`.
IMPORTANT: Simply using a model capable of generating images or speech will not be enough to generate that type of content. A setting of the proper class must be added when calling the `GemSpeakClient.ask_gemini` method.
Set the `settings` parameter in the `GemSpeakClient.ask_gemini` function, like so:
```
>>> res = cli.ask_gemini(
... 	model="<gemini model>",
... 	text="<text>",
... 	settings=<settings class>
... )
```
## TextGenSettings
The `TextGenSettings` class has the following parameters:
|Paremeter|Desc|Type|
|--|--|--|
|`code_execution`|Allow the model to generate and execute code. Active both in thinking and response.|`bool`|
|`perform_thinking`|Allow the model to generate thinking tokens. Set to `"AUTO"` to enable if available.|`bool, int`|
|`thinking_budget`|Limit the allowed number of thinking tokens. Set to `int` for a number, and `None` for automatic limit. | `int, None`|
|`perform_grounding`|Allow grounding with Google search|`bool`|
|`grounding_threshold`|Allow grounding threshold. Gemini will generate a grounding confidence based on whether it thinks is needs to have grounding, from 0 meaning not at all to 1 meaning definitely needs. Setting this value to `float` instead of `None` will enable grounding of the grounding confidence is greater than the grounding threshold.|`float, NoneType`|
|`url_context`|Allow the URL context tool|`bool`|
|`ignore_errors`|If the *gemspeak* library is temporarily out-of-date, enable this variable to prevent checking for setting validity. May cause unexpected errors directly from the `google.genai` library.|`bool`|
|`safety_settings`|The safety settings to use for the model.|`SafetySettings`|
Example usages of the `TextGenSettings` class:
```
>>> response = cli.ask_gemini(
...		model="gemini-2.5-flash-preview-04-17",
...		text="What is the sum of the first 1000 prime numbers?"
... 	settings=TextGenSettings(
... 		code_execution=True, # Allow code execution
... 		perform_thinking=True # Allow thinking
... 	)
... )
```
```
>>> response = cli.ask_gemini(
... 	model="gemini-2.0-flash",
... 	text="Tell me about WWII",
... 	settings=TextGenSettings(
... 		perform_grounding=True, # Allow Google grounding
... 		safety_settings=SafetySettings(
... 			dangerous_content="BLOCK MORE", # Block most dangerous content
... 			civic_integrity="BLOCK MOST" # Block some anti civic integrity content
... 		)
... 	)
... )
>>> response = cli.ask_gemini(
... 	model="gemini-1.5-flash",
... 	text="Who won FRC 2024?",
... 	settings=TextGenSettings(
... 		perform_grounding=True,
... 		grounding_threshold=0.7 # Only ground if highly confident
... 	)
... )
```
## Image Generation Settings
The `ImageGenSettings` class has the following parameters:
|Parameter|Desc|Type|
|--|--|--|
|`ignore_errors`|If the *gemspeak* library is temporarily out-to-date, enable this variable to prevent checking for setting validity. May cause unexpected errors directly from the `google.genai` library.|`bool`|
|`safety_settings`|The safety settings to use for the model.|`SafetySettings`|
Example usages of the `ImageGenSettings` class:

```
>>> res = cli.ask_gemini(
... 	model="gemini-2.0-flash-preview-image-generation",
... 	text="Make a picture of a mysterious castle.",
... 	settings=ImageGenSettings(),
... )
>>> image = res.image
>>> res.save_image(".")
```
```
>>> res = cli.ask_gemini(
... 	model="gemini-2.0-flash-preview-image-generation",
... 	text="Make a picture of an astronaut riding a horse.",
... 	settings=ImageGenSettings(
...			ignore_errors=True
... 	)
... )
>>> image = res.image
>>> res.save_image(".")
```
## Single-Speaker Text-To-Speech (TTS)
The `SingleSpeakerTTSSettings` class has the following parameters:
|Parameter|Desc|Type|
|--|--|--|
|`voice`|The Gemini voice to use. See the Gemini docs for all voices and descriptions.|`str`|
|`ignore_errors`|If the *gemspeak* library is temporarily out-to-date, enable this variable to prevent checking for setting validity. May cause unexpected errors directly from the `google.genai` library.|`bool`|
|`safety_settings`|The safety settings to use for the model.|`SafetySettings`|
Example usages of the `SingleSpeakerTTSSettings` class:
```
>>> res = cli.ask_gemini(
... 	model="gemini-2.5-flash-preview-tts",
... 	text="Say in a welcoming voice: Welcome to the gemspeak library!",
... 	settings=SingleSpeakerTTSSettings(
... 		voice="Kore"
... 	)
... )
>>> audio_bytes = res.audio
>>> res.save_audio(".")
```
```
>>> res = cli.ask_gemini(
... 	model="gemini-2.5-flash-preview-tts",
... 	text="Speak in a warm voice: Thank you for calling gemspeak support. Please wait for the next available agent. Our wait time is approximately seven hours. Please wait.",
... 	settings=SingleSpeakerTTSSettings(
... 		voice="Puck",
... 		safety_settings=SafetySettings(
... 			dangerous_content="BLOCK MOST"
... 	    )
...     )
... )
>>> audio_bytes = res.audio
>>> res.save_audio(".")
```
## Multi-Speaker TTS
The `MultiSpeakerTTSSettings` class has the following parameters:
|Parameter|Desc|Type|
|--|--|--|
|`speaker_names`|You must specify the names that are used in the input to show which speakers are saying which text. For example: `["Speaker 1", "Speaker 2"]`|`list[str]`|
|`voices`|The list of Gemini voice to use, in the same order as the speakers appear in the text. See the Gemini docs for all voices and descriptions.|`str`|
|`ignore_errors`|If the *gemspeak* library is temporarily out-of-date, enable this variable to prevent checking for setting validity. May cause unexpected errors directly from the `google.genai` library.|`bool`|
|`safety_settings`|The safety settings to use for the model.|`SafetySettings`|
Example usage of the `MultiSpeakerTTSSettings` class:
```
>>> res = cli.ask_gemini(
... 	model="gemini-2.5-flash-preview-tts",
... 	text="""Speak voice 1 in a confidential, quiet voice.
... Speak voice 2 in an interested voice.
... Voice 1: Pssst! Want to hear a secret?
... Voice 2: Oh, sure!
... Voice 1: Gemini TTS is really cool!""",
... 	settings=MultiSpeakerTTSSettings(
... 		speaker_names=["Voice 1", "Voice 2"],
... 		voices=["Charon", "Iapetus"]
... 	)
... )
>>> audio_bytes = res.audio
>>> res.save_audio(".")
```
# Uploading and Adding Files
*Gemspeak* provides support for three file upload classes: `LocalInlineImage`, `OnlineInlineImage`, and `FileUpload`. Any to all three can be used in one prompt.
## Inline Images
`LocalInlineImage` is for uploading local images under 20MB. Set the `path` parameter to the location of the image.
`OnlineInlineImage` is for uploading online images under 20MB. Set the `url` parameter to the source URL of the image, and the `ext` parameter to the file type of the image.
NOTE: Gemini only supports "PNG", "JPEG", "JPG", and "WEBP" for inline images.
### Creating Inline Images
This code shows how to create inline images:
```
>>> img1 = LocalInlineImage("C:\\Users\\username\\Pictures\\Screenshots\\Screenshot (22).png")
>>> img2 = OnlineInlineImage("https://inspireonline.in/products/iphone-16-myed3hn-a", "webp")
```
Upload the inline images by passing them to the `inline_images` parameter of `GemSpeakClient.ask_gemini`, as shown:
```
>>> res = cli.ask_gemini(
... 	model="gemini-2.0-flash",
... 	text="Compare the two uploaded images.",
... 	inline_images=[img1, img2]
... )
```
## File Upload
`FileUpload` is for files up to 20GB. The files must be local, and can be any of the supported file types. See the supported file types in the list `gemspeak.ALL_SUPPORTED_FILE_TYPES`. Set the `path` parameter to the local location of the file.
### Creating File Uploads
This code shows how to create file uploads:
```
>>> file1 = FileUpload("C:\\Users\\username\\Documents\\pdf_file.pdf")
>>> file2 = FileUpload("C:\\Users\\username\\Videos\\Recorded\\Video (15).mp4")
```
Upload the files by passing them to the `uploaded_files` parameter of `GemSpeakClient.ask_gemini`, as shown:
```
>>> res = cli.ask_gemini(
... 	model="gemini-2.0-flash",
... 	text="Analyze the PDF and MP4. file. Summarize both files.",
... 	uploaded_files=[file1, file2]
... )
```
# Embedding Content
Content embedding is converting text, images, and files to huge vectors to represent their meaning numerically. Use the `GemSpeakClient.embed_content` method to embed content. The inputs are exactly the same as the `GemSpeakClient.ask_gemini` method, and the output is a `gemspeak.response.GemSpeakEmbedResponse` which contains the embeddings in the `embeddings` variable.
Use the `ContentEmbeddingSettings` class for the settings. Set the `classification` to the classification type. Possible values: `["SEMANTIC_SIMILARITY", "CLASSIFICATION", "CLUSTERING",
"RETRIEVAL_DOCUMENT", "RETRIEVAL_QUERY", "QUESTION_ANSWERING", "FACT_VERIFICATION", "CODE_RETRIEVAL_QUERY"]`. See the Gemini docs for more information.

## Example Usage
Example usage of the `GemSpeakClient.embed_content` method:
```
>>> res = cli.embed_content(
... 	model="gemini-embedding-exp-03-07",
... 	text="What is the meaning of life?",
... 	inline_images=[LocalInlineImage("C:\\Users\\username\\Images\\image.png")],
... 	settings=ContentEmbeddingSettings(
... 		classification="SEMANTIC_SIMILARITY"
... 	)
... )
```
## Comparing Embeddings
The *gemspeak* library offers a tool to compare the embeddings of two pieces of content with the `GemSpeakClient.get_embed_distance` method. This compares the similarity in meaning of the two content pieces. It has similar inputs to the `GemSpeakClient.ask_gemini` function, but two `text` parameters, named `text1` and `text2`, two `inline_images` parameters named `inline_images1` and `inline_images2`, two `uploaded_files` parameters named `uploaded_files1` and `uploaded_files2`, and a `func` parameter of `callable` type, which is the function to compare the two outputs. To use your own functions, create a function that has two identically-sized lists of floats as parameters, and returns a float representing the distance between them by your own algorithm. By default, a N-dimensional Pythagorean theorem is used.
The function returns a list containing the distance, a `float`, and the two `gemspeak.responses.GemSpeakEmbedResponse` response objects of the embedding.
## Example Usage
Example usage of the `GemSpeakClient.embed_content` method:
```
>>> res = cli.get_embed_distance(
... 	model="text-embedding-004",
... 	text1="I threw a birthday party last night.",
... 	text2="Yesterday I threw a party to celebrate my birthday", # Should have similar meanings.
... 	settings=ContentEmbeddingSettings(
... 		classification="CLASSIFICATION"
... 	)
... )
>>> print(res[0])
<prints the distance float>
>>> print(res[1])
<prints the first embedding results>
>>> print(res[2])
<prints the second embedding results>
```
# Conversation
The `gemspeak.Conversation` class contains functions to create a conversation with Gemini, with multiple back-and-forth responses. Run

## Parameters
It has the following parameters:
|Paremeter|Desc|Type|
|--|--|--|
|`model`|The Gemini model id to use.|`str`|
|`system_prompt`|The system prompt to use to initialize the conversation. Change to change the context. Set to "" for no system prompt.|`str`|
|`warn_on_unconventional_speaker`|If True, will warn if a speaker is submitted that is not "USER", "ASSISTANT", or "SYSTEM".|`bool`|
|`client`|Optional. The client object to use. If not given, it must be given with the `generate_response` method.|`client, None`|
|`settings`|Either TextGenSettings or ImageGenSettings to use for the conversation.| `TextGenSettings, ImageGenSettings`|

## Initalization

Example initalization of the `gemspeak.Conversation` class from the client. Creating from the client will add the client to the conversation object and it will not need to be specified when calling `Conversation.generate_response`
```
>>> cli_conv = cli.create_conversation(
... 	model="gemini-2.0-flash",
... )
```

Example initalization of the `gemspeak.Conversation` class without the client. The client object must be passed to the `client` argument of the `Conversation.generate_response` function.
```
>>> regular_conv = Conversation(
... 	model="gemini-1.5-pro",
... 	settings=TextGenSettings(
... 		code_execution=True
... 	)
... )
```

## Methods

### `Conversation.add_contents`

Use `Conversation.add_contents` to add text for either side. Set `speaker` to the speaker name, and `text` to the text to add.
NOTE: Adding a `"USER"` content will NOT generate the AI response. You must use `Conversation.generate_response`.

### `Conversation.generate_response`

Use `Conversation.generate_response` to generate the response of the model to the current conversation. If the user has just spoken, Gemini will respond with it's response. However, if the assistant has just spoken, Gemini will likley impersonate the user and make up a follow-up question.

Example usage of `Conversation.add_contents` and `Conversation.generate_response`

```
>>> cli_conv.add_contents("USER", "What is 5 + 5?")
>>> cli_conv.add_contents("ASSISTANT", "5 + 5 is 11")
>>> cli_conv.add_contents("USER", "No it's not...")
>>> cli_conv.generate_contents()
>>> print(str(cli_conv))
```

# Versions

## 1.1.4
- Added adjustable grounding threshold to the `TextGenSettings` class.
- Added check to ensure thinking is enabeled for Gemini 2.5 Pro; it is required.
## 1.1.3
- Updated the data to reflect changes to the Gemini API rate limits
## 1.1.2
- Added `perform_thinking` parameter mode for `TextGenSettings` ability to be set as `"AUTO"`
- Fixed small documentation errors.
## 1.1.1
- Bug fix: `GemSpeakClient` was not importable via `gemspeak.GemSpeakClient` as documentation states.
## 1.1.0
- First release.