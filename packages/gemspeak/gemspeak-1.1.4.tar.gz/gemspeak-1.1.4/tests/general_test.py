from gemspeak.client import GemSpeakClient
from gemspeak.settings import *
from gemspeak.files import OnlineInlineImage, LocalInlineImage, FileUpload

# TESTS

cli = GemSpeakClient()

def simple_test():
    res = cli.ask_gemini(
        model="gemini-2.0-flash-lite",
        text="What can you do, Gemini?"
    )
    print(res)

def code_exec_test():
    res = cli.ask_gemini(
        model="gemini-2.0-flash",
        text="Find the sum of the first 100 prime numbers using a script",
        settings = TextGenSettings(
            code_execution=True
        )
    )
    print(res)

def tts_test():
    res = cli.ask_gemini(
        model = "gemini-2.5-flash-preview-tts",
        text="Say in a welcoming voice.\nSpeaker: Welcome to gemini text-to-speech!",
        settings=SingleSpeakerTTSSettings(
            voice="Kore",
        )
    )
    res.save_audio("C:\\Users\\paula\\OneDrive\\Documents\\Atticus's Stuff\\Python Files\\Maching Learning\\audio.wav")

def tts_multi_test():
    res = cli.ask_gemini(
        model = "gemini-2.5-flash-preview-tts",
        text="Say speaker 1 in a curious voice, and speaker 2 in an interested voice.\nSpeaker 1: Have you heard of Gemini text-to-speech?\nSpeaker 2: No! Tell me about it!",
        settings=MultiSpeakerTTSSettings(
            speaker_names=["Speaker 1", "Speaker 2"],
            voices=["Kore", "Puck"]
        )
    )
    res.save_audio("C:\\Users\\paula\\OneDrive\\Documents\\Atticus's Stuff\\Python Files\\Maching Learning\\multi_audio.wav")

def inline_image_local_test():
    inline_image = LocalInlineImage(
        path="C:\\Users\\paula\\OneDrive\\Pictures\\Screenshots\\Screenshot (52).png",
    )
    res = cli.ask_gemini(
        model="gemini-2.0-flash",
        text="What video game is the uploaded image from?",
        inline_images=[inline_image]
    )
    print(res)

def inline_image_online_test():
    inline_image = OnlineInlineImage(
        url="https://hips.hearstapps.com/hmg-prod/images/iphone-16-pro-pro-max-009-66eb07f9da260.jpg?crop=0.560xw:0.746xh;0.202xw,0.113xh&resize=980:*",
        ext="jpg"
    )
    res = cli.ask_gemini(
        model="gemini-2.0-flash",
        text="Analyse the uploaded image.",
        inline_images=[inline_image]
    )
    print(res)

def file_upload_test():
    file_upload = FileUpload(
        path="C:\\Users\\paula\\OneDrive\\Documents\\Atticus's Stuff\\Python Files\\Maching Learning\\TestPDF.pdf"
    )
    res = cli.ask_gemini(
        model="gemini-2.0-flash",
        text="Analyse the uploaded file. What is the text about?",
        uploaded_files=[file_upload]
    )
    print(res)

def image_gen_test():
    res = cli.ask_gemini(
        model="gemini-2.0-flash-preview-image-generation",
        text="Generate a Minecraft castle",
        settings=ImageGenSettings()
    )
    print(res)
    res.save_image("C:\\Users\\paula\\OneDrive\\Documents\\Atticus's Stuff\\Python Files\\Maching Learning\\image.png")

def text_embedding_test():
    res = cli.embed_content(
        model="gemini-embedding-exp-03-07",
        text="What is the meaning of life?"
    )
    print(res)

def text_embedding_distance_test():
    dist = cli.get_embed_distance(
        model="gemini-embedding-exp-03-07",
        text1="What is the meaning of life?",
        text2="Explain what the meaning of life in this universe is.",
    )
    print(dist[0])

def conversation_test():
    conv = cli.create_conversation(model="gemini-2.0-flash")

    conv.add_contents(
        speaker="USER",
        text="What is 5 + 5?"
    )
    conv.add_contents(
        speaker="ASSISTANT",
        text="5 + 5 is equal to 11."
    )
    conv.add_contents(
        speaker="USER",
        text="Are you sure?"
    )
    conv.generate_response()

    print(str(conv))

if __name__ == "__main__":
    #simple_test()
    #code_exec_test()
    #tts_test()
    #tts_multi_test()
    #inline_image_local_test()
    #inline_image_online_test()
    #file_upload_test()
    #image_gen_test()
    #text_embedding_test()
    #text_embedding_distance_test()
    #conversation_test()

    # Complete!