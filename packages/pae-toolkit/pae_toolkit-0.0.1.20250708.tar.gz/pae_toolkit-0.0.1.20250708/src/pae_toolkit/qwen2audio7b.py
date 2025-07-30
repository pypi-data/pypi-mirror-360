import os

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from io import BytesIO
from urllib.request import urlopen
import librosa
from transformers import Qwen2AudioForConditionalGeneration, AutoProcessor

MODEL_NAME = "Qwen/Qwen2-Audio-7B-Instruct"
processor = AutoProcessor.from_pretrained(MODEL_NAME)
model = Qwen2AudioForConditionalGeneration.from_pretrained(
    MODEL_NAME, device_map="auto"
)

conversation = [
    {
        "role": "user",
        "content": [
            {
                "type": "audio",
                "audio_url": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen2-Audio/audio/guess_age_gender.wav",
            },
        ],
    },
    {"role": "assistant", "content": "Yes, the speaker is female and in her twenties."},
    {
        "role": "user",
        "content": [
            {
                "type": "audio",
                "audio_url": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen2-Audio/audio/translate_to_chinese.wav",
            },
        ],
    },
]
text = processor.apply_chat_template(
    conversation, add_generation_prompt=True, tokenize=False
)
audios = []
for message in conversation:
    if isinstance(message["content"], list):
        audios.extend(
            [
                librosa.load(
                    BytesIO(urlopen(ele["audio_url"]).read()),
                    sr=processor.feature_extractor.sampling_rate,
                )[0]
                for ele in message["content"]
                if ele["type"] == "audio"
            ]
        )

inputs = processor(text=text, audios=audios, return_tensors="pt", padding=True)
inputs.input_ids = inputs.input_ids.to("cuda")

generate_ids = model.generate(**inputs, max_length=600)[:, inputs.input_ids.size(1) :]

response = processor.batch_decode(
    generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False
)[0]

print(f"Response:{response}")
