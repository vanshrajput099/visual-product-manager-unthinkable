from pydantic import BaseModel

class ImageUrlRequest(BaseModel):
    url: str

class Product_Model(BaseModel):
    title:str
    category:str
    price:int
    url:str
    features:list
    model:str
    desc:str
    color:str