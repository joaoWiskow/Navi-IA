from pathlib import Path
from tempfile import TemporaryDirectory
from PIL import Image, ImageDraw, UnidentifiedImageError
from visao import carregar_imagem

def executar_testes_de_estresse():
    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Teste 1: Arquivo corrompido / falso PNG
        arquivo_falso = tmp_path / "fake.png"
        arquivo_falso.write_bytes(b"Isto definitivamente nao sao pixels de uma imagem!")
        try:
            carregar_imagem(arquivo_falso)
            print("FALHA: O validador aceitou um arquivo corrompido!")
        except (UnidentifiedImageError, ValueError, OSError):
            print("PASS: Validador bloqueou o arquivo corrompido antes de chamar a API.")
            
        # Teste 2: Imagem valida gerada programaticamente com texto e ruido
        img_teste = Image.new("RGB", (400, 200), color="white")
        draw = ImageDraw.Draw(img_teste)
        draw.text((50, 80), "CODIGO: B-404", fill="black")
        
        caminho_ok = tmp_path / "valido.png"
        img_teste.save(caminho_ok)
        
        dados, mime, pil_img = carregar_imagem(caminho_ok)
        assert mime == "image/png"
        assert pil_img.size == (400, 200)
        print("PASS: Imagem sintetizada validada com sucesso pelo pipeline.")

if __name__ == "__main__":
    executar_testes_de_estresse()