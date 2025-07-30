import requests
from pic_prompt.builder import PicPrompt
from pic_prompt.core import PromptConfig
import json

PROMPT = """This is an image which contains information about one or more events.

Event Information:
Return a JSON object. Do not wrap the output in a code block or use markdown formatting. The JSON should have the following fields for each event:
{
    "event_name": "string",
    "event_date": "string", 
    "event_start_time": "string",
    "event_end_time": "string",
    "event_location": "string",
    "event_description": "string",
    "cost": "string",
    "organizer": "string",
    "contact_email": "string",
    "contact_phone": "string",
    "contact_website": "string",
    "event_url": "string",
    "notes": "string"
}
where:
- event_name: The name of the event.
- event_date: The date of the event. If the year is not specified, use 0000. Encode the date and time in the format YYYY-MM-DD.
- event_start_time: The start time of the event. Use the format HH:MM. Use the 24 hour format.
- event_end_time: The end time of the event. Use the format HH:MM. Use the 24 hour format.
- event_location: The location of the event.
- event_description: A short description of the event.
- cost: The cost of the event. This can be a string describing the cost.
- organizer: The name of the organizer or presenter.
- contact_email: The email to contact someone about the event.
- contact_phone: The phone number to contact someone about the event. The format should only include numbers with no dashed, parenthesis or whitespace. Example: '1234567890'.
- contact_website: The website of the event, organizer, or presenter.
- event_url: The URL of the event. Decode the QR code in the image to get the URL if needed.
- notes: Any additional notes about the event.

If any of the fields are not present in the image, return null for that field.
Return the JSON object as a string and nothing else.
Put anything other text in the notes field.
Do not include any text not in the image.

Event List:
Return all the events in the image as a list of JSON objects, like so:
{
    "event_list": [ <JSON object>, <JSON object>, ... ],
    "total_events": "integer"
}
"""


def make_gemini_request(api_key, prompt, image_url):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

    headers = {"Content-Type": "application/json"}

    gemini_config = PromptConfig(
        provider_name="gemini",
        model="gemini-2.0-exp-flash",
        max_tokens=3000,
        temperature=0.0,
    )
    builder = PicPrompt()
    builder.add_config(gemini_config)
    builder.add_user_message(PROMPT)
    builder.add_image_message(image_url)
    prompt_content = builder.get_content_for("gemini", preview=False)
    prompt_content_preview = builder.get_content_for("gemini", preview=True)
    prompt_content_json = json.dumps(prompt_content)
    print(json.dumps(prompt_content_preview, indent=4))

    response = requests.post(url, headers=headers, json=prompt_content)
    return response.json()


if __name__ == "__main__":
    image_url = "https://hstwhmjryocigvbffybk.supabase.co/storage/v1/object/public/promptfoo_images/hoa.jpg"
    api_key = "AIzaSyBXCVEvGCyy_8wK83s6TyehepDP4MfaELA"
    response = make_gemini_request(api_key, PROMPT, image_url)
    print(json.dumps(response, indent=4))
