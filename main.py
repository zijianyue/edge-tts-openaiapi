import asyncio
import configparser
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import APIKeyHeader
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import logging
from tools.edge_tts import generate_speech_async, get_voice
import re

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 读取配置文件
config = configparser.ConfigParser()
config.read('env.ini')

API_KEY = config['DEFAULT']['API_KEY']
DEFAULT_MALE_VOICE = config['DEFAULT']['DEFAULT_EDGETTS_MALE_VOICE']
DEFAULT_FEMALE_VOICE = config['DEFAULT']['DEFAULT_EDGETTS_FEMALE_VOICE']

app = FastAPI()

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

class SpeechRequest(BaseModel):
    model: str
    input: str
    voice: str
    response_format: str = "mp3"
    speed: float = 1.0

async def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key

# 辅助函数，用于清洗文本，移除特殊字符
def clean_text(text):
    # 这里使用正则表达式来替换掉特殊字符，比如'#'
    # 你可以根据需要添加更多要移除的字符
    cleaned_text = re.sub(r'#', '', text)
    return cleaned_text

@app.post("/v1/audio/speech")
async def create_speech(request: Request, speech_request: SpeechRequest, api_key: str = Depends(verify_api_key)):
    try:
        logger.info(f"Received request from {request.client.host} with parameters: {speech_request.dict()}")
        
        # 检查速度参数是否在有效范围内
        if speech_request.speed < 0.25 or speech_request.speed > 4.0:
            raise ValueError("Speed must be between 0.25 and 4.0")

        # 清洗输入文本，移除特殊字符
        cleaned_input = clean_text(speech_request.input)
        
        voice = get_voice(speech_request.voice, DEFAULT_MALE_VOICE, DEFAULT_FEMALE_VOICE)
        
        audio_stream = await generate_speech_async(
            text=cleaned_input, # 使用清洗后的文本
            voice=voice,
            speed=speech_request.speed,
            output_format=speech_request.response_format
        )

        return StreamingResponse(audio_stream, media_type=f"audio/{speech_request.response_format}")

    except ValueError as ve:
        logger.error(f"Invalid parameter: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=18759)