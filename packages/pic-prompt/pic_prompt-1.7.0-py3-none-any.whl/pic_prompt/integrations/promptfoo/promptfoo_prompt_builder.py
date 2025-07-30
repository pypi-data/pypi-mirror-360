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


def get_event_prompt(context: dict) -> list:
    """Returns the complete event extraction prompt structure with the given image URL"""
    provider: dict = context["provider"]
    provider_id: str = provider[
        "id"
    ]  # ex. openai:gpt-4o or bedrock:anthropic.claude-3-sonnet-20240229-v1:0
    is_anthropic: bool = "anthropic" in provider_id

    provider_label: str | None = provider.get(
        "label"
    )  # exists if set in promptfoo config.

    variables: dict = context["vars"]  # access the test case variables
    url: str = variables["url"]

    openai_config = PromptConfig(
        provider_name="openai",
        model="gpt-4o",
        max_tokens=3000,
        temperature=0.0,
    )
    builder = PicPrompt()
    builder.add_config(openai_config)
    builder.add_user_message(PROMPT)
    builder.add_image_message(url)
    prompt_content = builder.get_content_for("openai")
    return prompt_content


if __name__ == "__main__":
    # result =get_event_prompt({
    #     'provider': {
    #         'id': 'anthropic:messages:claude-3-opus-20240229',
    #         'label': 'Anthropic'
    #     },
    #     'vars': {'url': 'https://hstwhmjryocigvbffybk.supabase.co/storage/v1/object/public/promptfoo_images/all-pro-dadfs.PNG'}
    # })
    # print(json.dumps(result, indent=4))
    url = "https://hstwhmjryocigvbffybk.supabase.co/storage/v1/object/public/promptfoo_images/hoa.jpg"
    openai_config = PromptConfig(
        provider_name="openai",
        model="gpt-4o",
        max_tokens=3000,
        temperature=0.0,
    )
    builder = PicPrompt()
    builder.add_config(openai_config)
    builder.add_user_message(PROMPT)
    builder.add_image_message(url)
    prompt_content = builder.get_content_for("openai")
    print(prompt_content)

    # pm = PromptMessage(
    #     role=MessageRole.USER,
    #     content=[
    #         PromptContent(type=MessageType.TEXT, text=PROMPT),
    #         PromptContent(type=MessageType.IMAGE, image_url=url),
    #     ],
    # )
    # print(json.dumps(builder.build(), indent=4))
    # image_data = PromptBuilder._download_content(url)
    # print(f"Image data size: {len(image_data)}")
    # resized_image_data = PromptBuilder._resample_image(image_data)
    # print(f"PIL image size: {len(resized_image_data)}")
    # resized_image_data = PromptBuilder._resize_image(image_data, 1)
    # print(f"Resized image data size: {len(resized_image_data)}")
    # base64_data = PromptBuilder._get_base64_image(resized_image_data)
    # print(f"Base64 data size: {len(base64_data)}")
