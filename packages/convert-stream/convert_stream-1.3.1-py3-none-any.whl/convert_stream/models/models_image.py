#!/usr/bin/env python3
#
from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from PIL import Image
from cv2.typing import MatLike
import cv2
from soup_files import File


class LibraryImage(Enum):
    PIL = 1
    OPENCV = 2
    ROTATION_90 = 90
    ROTATION_180 = 180
    ROTATION_270 = 270


class ABCInvertColor(ABC):
    
    @abstractmethod
    def to_file(self, output_path:File):
        pass
 
    @abstractmethod
    def to_bytes(self) -> bytes:
        pass
        
    @abstractmethod
    def set_background_black(self):
        pass
    
    @abstractmethod
    def set_background_gray(self):
        pass
    
    @abstractmethod
    def set_gaussian_blur(self):
        pass
    

class ABCImageObject(ABC):
    """
    Classe abstrata base para objetos de imagem.
    """
    def __init__(self):
        super().__init__()
        self.current_library: LibraryImage = None
        self.width: int = 0
        self.height: int = 0
        
    @abstractmethod
    def is_paisagem(self) -> bool:
        """
        Retorna True se a imagem estiver em modo paisagem.
        """
        pass
    
    @abstractmethod
    def set_optimize(self, quality: int = 70):
        pass
    
    @abstractmethod
    def to_bytes(self) -> bytes:
        pass
    
    @abstractmethod
    def set_paisagem(self):
        pass
    
    @abstractmethod
    def set_rotation(self, rotation: LibraryImage = LibraryImage.ROTATION_180):
        pass
    
    @abstractmethod
    def set_background_gray(self):
        pass
    
    @abstractmethod
    def set_background_black(self):
        pass
    
    @abstractmethod
    def set_gaussian(self):
        pass
    
    @abstractmethod
    def to_image_pil(self) -> Image.Image:
        pass
    
    @abstractmethod
    def to_image_opencv(self) -> cv2.typing.MatLike:
        pass

    @abstractmethod
    def to_file(self, filepath: object):
        """
        Salva a imagem em um arquivo, garantindo modo paisagem.
        """
        pass
    

    