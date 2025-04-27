import os
from dotenv import load_dotenv
from openai import OpenAI
import json
import logging
from typing import Dict, List, Union, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

def openai_index(data: str, model: str = "gpt-4o-mini", max_retries: int = 3) -> Dict:
    """
    Process unstructured text data and convert it to structured JSON format.
    
    Args:
        data (str): Unstructured text data to process
        model (str): OpenAI model to use
        max_retries (int): Maximum number of retry attempts
        
    Returns:
        Dict: Structured data in JSON format
    """
    system_prompt = '''You are a highly skilled data structurer.

Here is a block of unstructured text containing contact information for various businesses. 
Your job is to carefully parse the text and output a clean, structured list of dictionaries in JSON format. 
Each dictionary should have the following fields:
- company_name
- contact_name
- title
- email
- phone_number
- type_of_business
- location
- last_contacted (use today's date if missing)
- notes

If any information is missing, leave the field as an empty string ("").
Ensure the output is valid JSON format with a "contacts" key containing an array of contact objects.
'''

    user_prompt = data

    for attempt in range(max_retries):
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0,
                max_tokens=2048,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                response_format={
                    "type": "json_object"
                }
            )
            ai_response = json.loads(completion.choices[0].message.content)
            
            # Validate response structure
            if not isinstance(ai_response, dict):
                raise ValueError("Response is not a dictionary")
                
            # Ensure the response has the expected structure
            if "contacts" not in ai_response:
                # If the response doesn't have a "contacts" key, wrap it in one
                ai_response = {"contacts": [ai_response]}
                
            return ai_response
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error (attempt {attempt+1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                raise ValueError(f"Failed to parse JSON response after {max_retries} attempts")
        except Exception as e:
            logger.error(f"Error during API call (attempt {attempt+1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                raise

def batch_process(data_list: List[str], model: str = "gpt-4o-mini") -> List[Dict]:
    """
    Process multiple data items in batch.
    
    Args:
        data_list (List[str]): List of unstructured text data to process
        model (str): OpenAI model to use
        
    Returns:
        List[Dict]: List of structured data in JSON format
    """
    results = []
    for i, data in enumerate(data_list):
        try:
            logger.info(f"Processing item {i+1}/{len(data_list)}")
            result = openai_index(data, model)
            results.append(result)
        except Exception as e:
            logger.error(f"Error processing item {i+1}: {e}")
            # Add empty result for failed items
            results.append({"contacts": []})
    
    return results

if __name__ == "__main__":
    # Example usage
    sample_data = """
    Company: Acme Corp
    Contact: John Doe
    Title: CEO
    Email: john@acmecorp.com
    Phone: 555-123-4567
    Type: Technology
    Location: New York, NY
    """
    
    try:
        result = openai_index(sample_data)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")
