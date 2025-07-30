from sskw.tasks.celery_app import app
from sskw.tasks.models import AudioTranscriptionRequest, AudioTranscriptionResult

@app.task(name="audio.transcription.paraformer.cpu")
def audio_transcription_paraformer_cpu(input: AudioTranscriptionRequest) -> AudioTranscriptionResult:
    """
    语音转文字 funasr的 paraformer模型 cpu版本

    参数:
    - input (AudioTranscriptionRequest): 输入数据结构
    
    返回:
    - AudioTranscriptionResult: 处理结果
    """

    raise NotImplementedError("此任务必须在具体实现中完成")

@app.task(name="audio.transcription.paraformer.gpu")
def audio_transcription_paraformer_gpu(input: AudioTranscriptionRequest) -> AudioTranscriptionResult:
    """
    语音转文字 funasr的 paraformer模型 GPU版本
    
    参数:
    - input (AudioTranscriptionRequest): 输入数据结构
    
    返回:
    - AudioTranscriptionResult: 处理结果
    """

    raise NotImplementedError("此任务必须在具体实现中完成")


@app.task(name="audio.transcription.sensevoice.cpu")
def audio_transcription_sensevoice_cpu(input: AudioTranscriptionRequest) -> AudioTranscriptionResult:
    """
    语音转文字 funasr的 sensevoice模型 cpu版本
    
    参数:
    - input (AudioTranscriptionRequest): 输入数据结构
    
    返回:
    - AudioTranscriptionResult: 处理结果
    """

    raise NotImplementedError("此任务必须在具体实现中完成")

@app.task(name="audio.transcription.sensevoice.gpu")
def audio_transcription_sensevoice_gpu(input: AudioTranscriptionRequest) -> AudioTranscriptionResult:
    """
    语音转文字 funasr的 sensevoice模型 GPU版本
    
    参数:
    - input (AudioTranscriptionRequest): 输入数据结构
    
    返回:
    - AudioTranscriptionResult: 处理结果
    """

    raise NotImplementedError("此任务必须在具体实现中完成")