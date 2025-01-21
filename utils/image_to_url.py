from fastapi import HTTPException
from io import BytesIO
from PIL import Image
import requests
import os
from utils.features import extract_image_category, find_similar_images

async def process_image_from_url(url: str):
    try:
        print(url)
        response = requests.get(url)
        response.raise_for_status()
        image_bytes = BytesIO(response.content)
        image = Image.open(image_bytes)
        temp_file_path = "temp_image.jpg"
        image.save(temp_file_path, "JPEG")
        predictions, features = extract_image_category(temp_file_path)
        similar_products = await find_similar_images(features.tolist(), predictions)
        os.remove(temp_file_path)
        return similar_products
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching the image: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing the image: {str(e)}")
