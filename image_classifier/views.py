from django.shortcuts import render
import json
from django.conf import settings
import requests
from .forms import ImageUploadForm
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


API_URL = "https://api-inference.huggingface.co/models/nateraw/food"
headers = {"Authorization": f"Bearer {settings.HF_API_KEY}"}

def image_classification_view(request):
    image_url = None  # Initialize to store the image URL

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = form.cleaned_data['image']

            # Save the uploaded image temporarily to the file system
            file_name = default_storage.save(f'temp/{image_file.name}', ContentFile(image_file.read()))
            image_url = default_storage.url(file_name)

            # Re-open the image file for the API request (reset file pointer)
            with default_storage.open(file_name, 'rb') as reopened_file:
                # Process the image and get classification results
                results = query_huggingface(reopened_file)

            return render(request, 'image_classifier/upload.html', {
                'results': results,
                'form': form,
                'image_url': image_url,  # Pass the image URL to the context
            })
    else:
        form = ImageUploadForm()

    return render(request, 'image_classifier/upload.html', {
        'form': form,
        'image_url': image_url,  # This will be None in GET requests
        'results': None  # No results in GET requests
    })

def query_huggingface(image_file):
    try:
        # Reset the file pointer to the beginning of the file
        image_file.seek(0)

        # Read the file content as bytes
        file_data = image_file.read()

        # Send the request to the Hugging Face API as a binary payload
        response = requests.post(API_URL, headers=headers, data=file_data, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses

        # Log the response content to the console
        print("Hugging Face API Response:", response.content)

        # Parse the JSON response
        result = response.json()

        # Log the parsed result to the console
        print("Parsed Result:", json.dumps(result, indent=4))

        return result
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response Content: {http_err.response.content}")
        return {"error": "An error occurred with the API request."}
    except requests.exceptions.RequestException as req_err:
        print(f"Request failed: {req_err}")
        return {"error": str(req_err)}