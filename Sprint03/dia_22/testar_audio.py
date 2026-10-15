import wave
from pathlib import Path
from tempfile import TemporaryDirectory
from transcrever import transcrever_audio

def executar_testes_de_estresse():
    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Teste 1: Arquivo WAV com 3 segundos de silencio absoluto (amplitude zero)
        silencio_wav = tmp_path / "silencio.wav"
        with wave.open(str(silencio_wav), "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(16000)
            f.writeframes(b"\x00\x00" * (16000 * 3))
            
        try:
            transcrever_audio(silencio_wav)
            print("FALHA: O sistema processou um audio mudo sem reclamar!")
        except ValueError as erro:
            if "silencioso" in str(erro).lower():
                print("PASS: Audio silencioso barrado com sucesso pela deteccao de energia RMS.")
            else:
                print(f"PASS: Falha capturada corretamente: {erro}")

if __name__ == "__main__":
    executar_testes_de_estresse()
    