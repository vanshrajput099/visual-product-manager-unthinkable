from sklearn.metrics.pairwise import cosine_similarity
import tensorflow as tf
import numpy as np
from typing import List, Dict, Tuple
from db.db import collection

def extract_image_category(img_path: str, top_n: int = 3) -> Tuple[List[Dict[str, float]], np.ndarray]:
    model = tf.keras.applications.MobileNet(weights="imagenet")
    img = tf.keras.preprocessing.image.load_img(img_path, target_size=(224, 224))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = tf.keras.applications.mobilenet.preprocess_input(img_array)
    feature_extractor = tf.keras.Model(inputs=model.input, outputs=model.layers[-2].output) 
    features = feature_extractor.predict(img_array) 
    predictions = model.predict(img_array)
    decoded_predictions = tf.keras.applications.mobilenet.decode_predictions(predictions, top=top_n)[0]
    result = [{"category": pred[1], "probability": float(pred[2])} for pred in decoded_predictions]
    return result, features.flatten()

async def find_similar_images(
    input_features: List[float],
    input_categories: List[Dict[str, float]],
    top_n: int = 10  
):
    
    all_products = await collection.find().to_list(length=None)
    results = []

    for image in all_products:
        
        db_features = np.array(image["features"])
        db_category = image["category"] 

        feature_similarity = cosine_similarity(
            [input_features], [db_features]
        )[0][0]

        category_similarity = 0
        for input_cat in input_categories:
            if input_cat["category"] == db_category:
                category_similarity += input_cat["probability"]

        combined_score = feature_similarity + category_similarity
        results.append({
            "url": image["url"],  
            "combined_score": combined_score,
            "title": image["title"],
            "category": image["category"],
            "price": image["price"],
            "features": image.get("features"),
            "model": image.get("model"), 
            "desc": image.get("desc"),
            "color": image.get("color",None)
        })

    # Sort results by combined score in descending order and return the top N results
    results = sorted(results, key=lambda x: x["combined_score"], reverse=True)
    return results[:top_n]