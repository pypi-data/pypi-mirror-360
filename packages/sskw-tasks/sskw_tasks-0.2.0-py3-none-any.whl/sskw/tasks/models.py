from pydantic import BaseModel
from typing import List, Dict


class AudioTranscriptionRequest(BaseModel):
    audio_urls: List[str]
    data_id: str    

class AudioTranscriptionResult(BaseModel):
    audio_urls: List[str]
    data_id: str
    segments: List[Dict[str, str]]
    merged_audio_url: str


class AudioFormatConversionRequest(BaseModel):
    from_url: str
    from_format: str
    to_format: str
    data_id: str

class AudioFormatConversionResult(BaseModel):
    from_url: str
    from_format: str
    to_format: str
    data_id: str
    to_url: str

