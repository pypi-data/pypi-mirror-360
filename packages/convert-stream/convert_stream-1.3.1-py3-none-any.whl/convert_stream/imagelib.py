#!/usr/bin/env python3
#
from __future__ import annotations
from typing import Tuple
from io import BytesIO
from PIL import Image, ImageOps, ImageFilter
from cv2.typing import MatLike
import cv2
import numpy as np
from soup_files import File
from convert_stream.models.models_image import LibraryImage, ABCImageObject, ABCInvertColor

#=============================================================================#
# Inverter cores em imagens
#=============================================================================#


class ImplementInvertColorOpenCv(ABCInvertColor):
    """
        Escurecer texto em imagens.
    """
    def __init__(self, image_bytes: bytes):
        super().__init__()
        if not isinstance(image_bytes, bytes):
            raise ValueError(f'{__class__.__name__}\nUse: bytes, não {type(image_bytes)}')
        self.image_bytes: bytes = image_bytes
        
    def _image_bytes_to_opencv(self, img_bytes: bytes) -> MatLike:
        """Converte os bytes de uma imagem em objeto opencv MatLike"""
        nparr = np.frombuffer(img_bytes, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
    def _image_opencv_tobytes(self, img:MatLike) -> bytes:
        """Convert um objeto opencv MatLike em bytes de imagem"""
        # Codifica como PNG (ou use '.jpg' para JPEG)
        _, buffer = cv2.imencode('.png', img)
        # Obtém os bytes da imagem
        return buffer.tobytes()
        
    def set_gaussian_blur(self):
        # Aplica um filtro Gaussiano para reduzir o ruído
        _blurred: MatLike = cv2.GaussianBlur(
            self._image_bytes_to_opencv(self.image_bytes),
            (3, 3),
            0.5
        )
        self.image_bytes = self._image_opencv_tobytes(_blurred)

    def __set_background_black(self):
        # Aplica binarização adaptativa (texto branco, fundo preto)
        binary: MatLike = cv2.adaptiveThreshold(
            self._image_bytes_to_opencv(self.image_bytes),
            150,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,  
            11,
            2
        )
        self.image_bytes = self._image_opencv_tobytes(binary)
        
    def __set_background_gray(self):
        # Aplica binarização adaptativa (texto preto, fundo branco)
        _binary = cv2.adaptiveThreshold(
            self._image_bytes_to_opencv(self.image_bytes),
            150,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,  # Inverte o texto para ser branco inicialmente
            11,
            2
        )
        self.image_bytes = self._image_opencv_tobytes(_binary)

    def set_background_black(self):
        self.set_gaussian_blur()
        self.__set_background_black()
        _result: MatLike = cv2.bitwise_not(self._image_bytes_to_opencv(self.image_bytes))
        self.image_bytes = self._image_opencv_tobytes(_result)
        
    def set_background_gray(self):
        self.set_gaussian_blur()
        self.__set_background_gray()
        _result: MatLike = cv2.bitwise_not(self._image_bytes_to_opencv(self.image_bytes))
        self.image_bytes = self._image_opencv_tobytes(_result)

    def to_file(self, output_path: File):
        print(f'Salvando: {output_path.basename()}')
        cv2.imwrite(output_path.absolute(), self._image_bytes_to_opencv(self.image_bytes))
        
    def to_bytes(self) -> bytes:
        return self.image_bytes
            
    def to_pil(self) -> Image.Image: 
        """Converte a propriedade bytes em imagem PIL"""   
        return Image.open(BytesIO(self.image_bytes))
    
    def to_opencv(self) -> cv2.typing.MatLike:
        """Converte a propriedade bytes em imagem objeto opencv"""  
        return self._image_bytes_to_opencv(self.image_bytes)
      
      
class ImplementInvertColorPIL(ABCInvertColor):
    """
        Implementação da inversão de cores usando PIL (Pillow).
    """
    def __init__(self, image_bytes:bytes):
        super().__init__()
        if not isinstance(image_bytes, bytes):
            raise ValueError(f'{__class__.__name__}\nUse: bytes, não {type(image_bytes)}')
        self.image_bytes: bytes = image_bytes
        
    def set_gaussian_blur(self):
        img_pil = Image.open(BytesIO(self.image_bytes))
        # Aplicar um desfoque semelhante ao cv2.GaussianBlur
        blurred: Image.Image = img_pil.filter(ImageFilter.GaussianBlur(radius=1))
        buff = BytesIO()
        blurred.save(buff, 'PNG')
        self.image_bytes = buff.getvalue()
        buff.close()
        
    def set_background_black(self):
        img_pil = Image.open(BytesIO(self.image_bytes))
        _result = ImageOps.invert(img_pil.convert("L")) # Converte para escala de cinza
        buff = BytesIO()
        _result.save(buff, 'PNG')
        self.image_bytes = buff.getvalue()
        buff.close()

    def set_background_gray(self):
        # Abrir a imagem a partir dos bytes
        img_pil = Image.open(BytesIO(self.image_bytes))

        # Converter para escala de cinza
        gray_img = img_pil.convert("L")

        # Inverter as cores
        inverted_img = ImageOps.invert(gray_img)

        # Aplicar um threshold invertido: força fundo branco e texto preto
        threshold = 128  # Ajuste conforme necessário
        binary_img = inverted_img.point(lambda x: 0 if x > threshold else 150)  # Invertido aqui!

        # Salvar de volta para bytes
        buff = BytesIO()
        binary_img.save(buff, 'PNG')
        self.image_bytes = buff.getvalue()
        buff.close()
        
    def to_file(self, output_path: File):
        img: Image.Image = Image.open(self.image_bytes)
        img.save(output_path.absolute(), 'PNG')

    def to_bytes(self) -> bytes:
        buff_img = BytesIO()
        Image.open(BytesIO(self.image_bytes)).save(buff_img, 'PNG')
        bytes_img = buff_img.getvalue()
        buff_img.close()
        return bytes_img
    
    def to_pil(self) -> Image:
        return Image.open(BytesIO(self.image_bytes))


class ImageInverColor(ABCInvertColor):
    """
        Escurecer texto em imagens.
    """
    def __init__(self, invert_color: ABCInvertColor):
        if not isinstance(invert_color, ABCInvertColor):
            raise ValueError(f'{__class__.__name__}\nUse: ABCInvertColor(), não {type(invert_color)}')
        self.invert_color:ABCInvertColor = invert_color
        
    def set_gaussian_blur(self):
        self.invert_color.set_gaussian_blur()
        
    def set_background_black(self):
        self.invert_color.set_background_black()
        
    def set_background_gray(self):
        self.invert_color.set_background_gray()

    def to_file(self, output_path:File):
        return self.invert_color.to_file(output_path)
    
    def to_bytes(self):
        return self.invert_color.to_bytes()
    
    @classmethod
    def create_from_file(
                    cls, f: File, *,
                    library: LibraryImage = LibraryImage.OPENCV
            ) -> ImageInverColor:
        img: ImageObject = ImageObject.create_from_file(f, library=library)
        if library == LibraryImage.OPENCV:
            inv: ABCInvertColor = ImplementInvertColorOpenCv(f.path.read_bytes())
        elif library == LibraryImage.PIL:
            inv: ABCInvertColor = ImplementInvertColorPIL(f.path.read_bytes())
        else:
            raise NotImplementedError(
                f'{__class__.__name__}\nUse: LibraryImage.OPENCV, ou LibraryImage.PIL, não {type(library)}'
            )
        return cls(inv)
    
    @classmethod
    def create_from_bytes(
                cls, bt: bytes, *,
                library: LibraryImage = LibraryImage.OPENCV
            ) -> ImageInverColor:
        if library == LibraryImage.OPENCV:
            invert_color: ABCInvertColor = ImplementInvertColorOpenCv(bt)
        elif library == LibraryImage.PIL:
            invert_color: ABCInvertColor = ImplementInvertColorPIL(bt)
        else:
            raise NotImplementedError(
                f'{__class__.__name__}\nUse: LibraryImage.OPENCV, ou LibraryImage.PIL, não {type(library)}'
            )
        return cls(invert_color)


#=============================================================================#
# Manipulação de imagens
#=============================================================================#


class ImageObjectPIL(ABCImageObject):
    """
        Implementação de ImageObject usando PIL.
    """
    def __init__(self, image_bytes: bytes):
        super().__init__()
        if not isinstance(image_bytes, bytes):
            raise ValueError(f'{__class__.__name__} Use: bytes, não {type(image_bytes)}')
        self.current_library = LibraryImage.PIL
        self.image_bytes = image_bytes
        self.max_size: Tuple[int, int] = (1980, 720) # Dimensões máximas, altere se necessário.
        
        try:
            image_pil = Image.open(BytesIO(image_bytes))
        except Exception as e:
            raise ValueError(f"{__class__.__name__}\nPIL: Bytes de imagem inválidos")
        else:
            self.dimensions = image_pil.size

        # Redimensionar, se as dimensões estiverem maior que self.max_size.
        if (image_pil.width > self.max_size[0]) or (image_pil.height > self.max_size[1]):
            #print(f'{__class__.__name__} Redimensionando imagem [{self.dimensions}], aguarde...')
            buff_image: BytesIO = BytesIO()
            image_pil.save(buff_image, format='PNG', optimize=True, quality=80)
            image_pil = Image.open(buff_image)
            self.dimensions = image_pil.size
            self.image_bytes = buff_image.getvalue()
            buff_image.seek(0)
            buff_image.close()
            del buff_image
            #print(f'{__class__.__name__} Nova dimensão [{self.dimensions}]')
        self.width = image_pil.width
        self.height = image_pil.height
        del image_pil
            
    def is_paisagem(self) -> bool:
        """
        Retorna True se a imagem estiver em modo paisagem.
        """
        width, height = self.dimensions
        return width > height
    
    def set_rotation(self, rotation: LibraryImage = LibraryImage.ROTATION_180):
        img = Image.open(BytesIO(self.image_bytes))
        if rotation == LibraryImage.ROTATION_90:
            img = img.transpose(Image.Transpose.ROTATE_90) 
        elif rotation == LibraryImage.ROTATION_180:
            img = img.transpose(Image.Transpose.ROTATE_180)
        elif rotation == LibraryImage.ROTATION_270:
            img = img.transpose(Image.Transpose.ROTATE_270)
        else:
            return
        new_bytes = BytesIO()
        img.save(new_bytes, format='PNG')
        self.image_bytes = new_bytes.getvalue()
        
    def set_paisagem(self):
        if not self.is_paisagem():
            img = Image.open(BytesIO(self.image_bytes))
            img = img.transpose(Image.Transpose.ROTATE_90) # Rotaciona -90 graus
            new_bytes = BytesIO()
            img.save(new_bytes, format='PNG')
            self.image_bytes = new_bytes.getvalue()
            
    def set_optimize(self, quality: int = 70):
        optimized_bytes = BytesIO()
        img = self.to_image_pil()
        img.save(optimized_bytes, format='PNG', optimize=True, quality=quality)
        self.image_bytes = optimized_bytes.getvalue()
        
    def set_background_black(self):
        inv = ImageInverColor.create_from_bytes(self.to_bytes(), library=LibraryImage.PIL)
        inv.set_background_black()
        self.image_bytes = inv.to_bytes()
    
    def set_background_gray(self):
        inv = ImageInverColor.create_from_bytes(self.to_bytes(), library=LibraryImage.PIL)
        inv.set_background_gray()
        self.image_bytes = inv.to_bytes()
        
    def set_gaussian(self):
        inv = ImageInverColor.create_from_bytes(self.to_bytes(), library=LibraryImage.PIL)
        inv.set_gaussian_blur()
        self.image_bytes = inv.to_bytes()
    
    def to_image_pil(self) -> Image.Image:
        return Image.open(BytesIO(self.image_bytes))
    
    def to_image_opencv(self) -> cv2.typing.MatLike:
        nparr = np.frombuffer(self.image_bytes, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    def to_bytes(self) -> bytes:
        img = self.to_image_pil()   
        image_bytes = BytesIO()
        img.save(image_bytes, format='PNG')
        return image_bytes.getvalue()
        
    def to_file(self, filepath: str):
        try:
            self.to_image_pil().save(filepath)
        except ImportError:
            raise ImportError("A biblioteca PIL não está instalada. Instale-a com 'pip install Pillow'.")
        except Exception as e:
            raise Exception(f"Erro ao salvar imagem PIL: {e}")


class ImageObjectOpenCV(ABCImageObject):
    """
        Implementação de ImageObject usando OpenCV.
    """
    def __init__(self, image_bytes):
        super().__init__()
        if not isinstance(image_bytes, bytes):
            raise ValueError(f'{__class__.__name__} Use: bytes, não {type(image_bytes)}')
        self.current_library = LibraryImage.OPENCV
        self.image_bytes = image_bytes
        self.max_size: Tuple[int, int] = (1980, 720)
        
        try:
            nparr = np.frombuffer(self.image_bytes, np.uint8)
            image_opencv: MatLike = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        except Exception as e:
            print('-' * 80)
            raise ValueError(f"\nCV2: Bytes de imagem OpenCV inválidos")
        else:
            self.dimensions = (image_opencv.shape[1], image_opencv.shape[0])  # (largura, altura)
        
        # Redimensionar se necessário
        if (self.dimensions[0] > self.max_size[0]) or (self.dimensions[1] > self.max_size[1]):
            #print(f'{__class__.__name__} Redimensionando imagem [{self.dimensions}], aguarde...')
            h, w = image_opencv.shape[:2]
            scale = min(self.max_size[0] / w, self.max_size[1] / h)
            new_size = (int(w * scale), int(h * scale))
            image_opencv = cv2.resize(image_opencv, new_size, interpolation=cv2.INTER_LANCZOS4)
            self.dimensions = (image_opencv.shape[1], image_opencv.shape[0])
            #print(f'{__class__.__name__} Nova dimensão [{self.dimensions}]')
        # Converter a imagem de volta para bytes
        _, encoded_img = cv2.imencode('.png', image_opencv)
        self.image_bytes = encoded_img.tobytes()
        # Atualizar dimensões após redução
        self.height = self.dimensions[0]
        self.width = self.dimensions[1]
        
    def is_paisagem(self) -> bool:
        """
        Retorna True se a imagem estiver em modo paisagem.
        """
        width, height = self.dimensions
        return width > height
    
    def set_rotation(self, rotation: LibraryImage = LibraryImage.ROTATION_180):
        nparr = np.frombuffer(self.image_bytes, np.uint8)
        img:MatLike = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if rotation == LibraryImage.ROTATION_90:
            img:MatLike = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif rotation == LibraryImage.ROTATION_180:
            img:MatLike = cv2.rotate(img, cv2.ROTATE_180) 
        elif rotation == LibraryImage.ROTATION_270:
            img:MatLike = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
            img:MatLike = cv2.rotate(img, cv2.ROTATE_180)
        else:
            return
        success, encoded_image = cv2.imencode('.png', img)
        if success:
            self.image_bytes = encoded_image.tobytes()
            
    def set_paisagem(self):
        if not self.is_paisagem():
            nparr = np.frombuffer(self.image_bytes, np.uint8)
            img:MatLike = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            img:MatLike = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE) # Rotaciona -90 graus
            
            success, encoded_image = cv2.imencode('.png', img)
            if success:
                self.image_bytes = encoded_image.tobytes()
                
    def set_optimize(self, quality: int = 70):
        """
            Reduz o tamanho da imagem, e salva a imagen reduzida na propriedade bytes.
        """
        imagem: MatLike = self.to_image_opencv()
        _status, buffer = cv2.imencode(".png", imagem, [cv2.IMWRITE_JPEG_QUALITY, quality])
        if _status:
            self.image_bytes = buffer.tobytes()
            
    def set_background_black(self):
        inv = ImageInverColor.create_from_bytes(self.to_bytes(), library=LibraryImage.OPENCV)
        inv.set_background_black()
        self.image_bytes = inv.to_bytes()
    
    def set_background_gray(self):
        inv = ImageInverColor.create_from_bytes(self.to_bytes(), library=LibraryImage.OPENCV)
        inv.set_background_gray()
        self.image_bytes = inv.to_bytes()
        
    def set_gaussian(self):
        inv = ImageInverColor.create_from_bytes(self.to_bytes(), library=LibraryImage.OPENCV)
        inv.set_gaussian_blur()
        self.image_bytes = inv.to_bytes()
    
    def to_image_pil(self) -> Image.Image:
        return Image.open(BytesIO(self.image_bytes))
    
    def to_image_opencv(self) -> cv2.typing.MatLike:
        nparr = np.frombuffer(self.image_bytes, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    def to_bytes(self) -> bytes: 
        _, buffer = cv2.imencode('.png', self.to_image_opencv())  # Codifica como PNG (ou use '.jpg' para JPEG)
        return buffer.tobytes()

    def to_file(self, filepath: str):
        try:
            img = self.to_image_opencv()
            cv2.imwrite(filepath, img)
        except ImportError:
            raise ImportError("A biblioteca OpenCV não está instalada. Instale-a com 'pip install opencv-python'.")
        except Exception as e:
            raise Exception(f"Erro ao salvar imagem OpenCV: {e}")


class ImageObject(object):
    """
        Facade para manipular imagens com PIL ou OPENCV
    """
    def __init__(self, img_obj: ABCImageObject):
        super().__init__()
        self.img_obj: ABCImageObject = img_obj
        self.current_library: LibraryImage = self.img_obj.current_library

    @property
    def width(self) -> int:
        return self.img_obj.width

    @property
    def height(self) -> int:
        return self.img_obj.height

    def set_optimize(self, quality: int = 70):
        """
            Reduz o tamanho da imagem, e salva a imagen reduzida na propriedade bytes.
        """
        self.img_obj.set_optimize(quality)
        
    def set_rotation(self, rotation: LibraryImage = LibraryImage.ROTATION_180):
        self.img_obj.set_rotation(rotation)
        
    def set_paisagem(self):
        self.img_obj.set_paisagem()
        
    def set_background_gray(self):
        self.img_obj.set_background_gray()
        
    def set_background_black(self):
        self.img_obj.set_background_black()
        
    def set_gaussian(self):
        self.img_obj.set_gaussian()
            
    def to_image_pil(self) -> Image.Image:
        return self.img_obj.to_image_pil()
    
    def to_image_opencv(self) -> cv2.typing.MatLike:
        return self.img_obj.to_image_opencv()
        
    def to_file(self, f: File):
        self.img_obj.to_file(f.absolute())
    
    def is_paisagem(self) -> bool:
        return self.img_obj.is_paisagem()
    
    def to_bytes(self) -> bytes:
        return self.img_obj.to_bytes()

    @classmethod
    def create_from_bytes(
                cls, image_bytes: bytes, *,
                library: LibraryImage = LibraryImage.OPENCV
            ) -> ImageObject:
        if library == LibraryImage.PIL:
            img = ImageObjectPIL(image_bytes)
        elif library == LibraryImage.OPENCV:
            img = ImageObjectOpenCV(image_bytes)
        else:
            raise ValueError("Biblioteca de imagem inválida.")
        return cls(img)

    @classmethod
    def create_from_file(
                cls, filepath: File, *,
                library: LibraryImage = LibraryImage.OPENCV
            ) -> ImageObject:
        try:
            if library == LibraryImage.PIL:
                image = ImageObjectPIL(filepath.path.read_bytes())
            elif library == LibraryImage.OPENCV:
                image = ImageObjectOpenCV(filepath.path.read_bytes())
            else:
                raise ValueError("Biblioteca de imagem inválida.")
        except FileNotFoundError:
            print(f'O arquivo não existe: {filepath.absolute()}')
            raise
        except Exception as e:
            print(e, '\n')
            print('=' * 70)
            raise ValueError(f'{__class__.__name__} Arquivo inválido: [{filepath.absolute()}]')
        return cls(image)
       

