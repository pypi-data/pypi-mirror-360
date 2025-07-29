from gtts import gTTS, lang # need pip install gTTS
import time
import os
import playsound # need pip install playsound==1.2.2 (the later version wouldn't work)
from multiprocessing.managers import Namespace

def gtts_speak(text: str = None, lang: str = 'vi', shared_name: Namespace = None) -> str:
    if text is None:
        raise ValueError("text could not be None, did you forget what to speak?")
    elif not isinstance(text, str):
        raise TypeError("text must be str")
    temp_filename = str(round(time.time() * 10)) + ".mp3"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    temp_ID_path = os.path.join(script_dir, temp_filename)

    tts = gTTS(text=text, lang=lang)
    tts.save(temp_ID_path)

    if shared_name is not None:
        shared_name.path = temp_ID_path #shared_name.path will store the file path, enabling cleanup if the multiprocessing process is terminated prematurely.

    try:
        playsound.playsound(temp_ID_path)
    finally:
        if os.path.exists(temp_ID_path):
            os.remove(temp_ID_path)

    return temp_ID_path

#for those who need what language it supports and the code lang for it
def gtts_print_supported_languages() -> None:
    supported_languages = lang.tts_langs()  # Get the dictionary of supported languages
    print("Supported languages by gTTS:")
    for code, language in supported_languages.items():
        print(f"{code}: {language}")

#how to use
if __name__=="__main__":
    gtts_print_supported_languages()
    _temp_ID = gtts_speak("Xin chào người đẹp, em tên là gì thế", "vi")
    print("You can get file name as output: "+ _temp_ID)
    
    from multiprocessing import Process, Manager
    _manager = Manager()
    _namespace = _manager.Namespace()
    _namespace.path = ""

    _p = Process(target=gtts_speak, args=("Xin chào bạn, mình là An, hiện là học sinh lớp 12 trường trung học phổ thông chuyên", "vi", _namespace))
    _p.start()
    time.sleep(3)
    _p.terminate()
    _p.join()

    print("Path from shared namespace:", _namespace.path)
    if os.path.exists(_namespace.path):
        os.remove(_namespace.path)
        print("Cleaned up leftover file.")
    else:
        print("No file to clean up.")