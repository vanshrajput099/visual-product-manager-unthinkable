import uvicorn
from utils.image_to_url import process_image_from_url
from models.model import Product_Model
from db.db import collection
import os
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
from fastapi.responses import JSONResponse
from utils.features import extract_image_category, find_similar_images
from models.model import ImageUrlRequest
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

origins = [os.getenv("FRONTEND_URL")]

app.add_middleware(
    CORSMiddleware,
    allow_origins= origins,
    allow_credentials = True,
    allow_methods = ['*'],
    allow_headers = ['*']
)

async def getAllProducts():
    data = []
    cursor = collection.find({})
    async for document in cursor:
        document["_id"] = str(document["_id"])
        document["price"] = int(document.get("price", 0)) if document.get("price") else None
        document["model"] = document.get("model") or "Unknown"
        document["color"] = document.get("color") or "Unknown"
        data.append(Product_Model(**document))
    return data

@app.get("/")
async def get_products():
    response = await getAllProducts()
    return [image.dict() for image in response]

@app.post("/image/url")
async def image_url(request: ImageUrlRequest):
    url = request.url
    if not url:
        raise HTTPException(status_code=400, detail="URL must be provided.")
    similar_products = await process_image_from_url(url)
    return JSONResponse(content={"data": similar_products})

@app.post("/image/upload")
async def image_upload(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(("jpg", "jpeg", "png")):
        raise HTTPException(status_code=400, detail="Only JPG, JPEG, and PNG files are allowed.")
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        predictions, features = extract_image_category(temp_file_path)
        similar_products = await find_similar_images(features.tolist(), predictions)
        return JSONResponse(content={"data": similar_products})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing the image: {str(e)}")
    finally:
        os.remove(temp_file_path)    




# This is the code I Used to Enter Data In Database - From An Array ;
        
# def convert_booleans(data_list):
#     for item in data_list:
#         for key, value in item.items():
#             if isinstance(value, bool):
#                 item[key] = "true" if value else "false"
#     return data_list

# @app.post("/add")
# async def route():
#     import os
#     import requests
#     import re
     
#     try:
#         for product in data:
#             image_url = product["image"]
#             response = requests.get(image_url, stream=True)
#             if response.status_code == 200:
#                 sanitized_title = re.sub(r"[^\w.-]", "_", product["title"])  # Perform sanitization
#                 temp_file_path = f"temp_{sanitized_title}.jpg"
#                 with open(temp_file_path, "wb") as buffer:
#                     for chunk in response.iter_content(1024):
#                         buffer.write(chunk)
#             else:
#                 raise HTTPException(status_code=400, detail=f"Failed to download image: {image_url}")

#             predictions, features = extract_image_category(temp_file_path)

#             product_data = {
#                 "title": product["title"],
#                 "category": product["category"],
#                 "price": product["price"],
#                 "url": product.get("image"),
#                 "features": features.tolist(),
#                 "model": product.get("model",None),  # Use `get` to avoid KeyError
#                 "desc": product.get("description"),
#                 "color": product.get("color",None)# Use `get` to avoid KeyError
#             }
#             await collection.insert_one(product_data)
#             os.remove(temp_file_path)
        
#         return JSONResponse(content={"message": "Products added successfully."})
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing products: {str(e)}")
    
#     finally:
#         print("Finished processing all products.")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)