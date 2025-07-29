"""
DACP JSON Parser - Robust JSON parsing for agent responses.

This module provides enhanced JSON parsing capabilities that can handle
various LLM response formats and provide intelligent fallbacks.
"""

import json
import re
import logging
from typing import Dict, Any, Optional, Union
from pydantic import BaseModel

logger = logging.getLogger("dacp.json_parser")


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON from text using multiple strategies.
    
    Args:
        text: Raw text that might contain JSON
        
    Returns:
        Parsed JSON dict or None if no valid JSON found
    """
    if not isinstance(text, str):
        return None
    
    logger.debug(f"🔍 Attempting to extract JSON from text: {text[:100]}...")
    
    # Strategy 1: Try parsing the entire text as JSON
    try:
        result = json.loads(text.strip())
        logger.debug("✅ Successfully parsed entire text as JSON")
        return result
    except json.JSONDecodeError:
        logger.debug("❌ Failed to parse entire text as JSON")
    
    # Strategy 2: Find JSON between braces
    json_start = text.find('{')
    json_end = text.rfind('}') + 1
    if json_start >= 0 and json_end > json_start:
        json_str = text[json_start:json_end]
        try:
            result = json.loads(json_str)
            logger.debug("✅ Successfully extracted JSON between braces")
            return result
        except json.JSONDecodeError:
            logger.debug("❌ Failed to parse JSON between braces")
    
    # Strategy 3: Find JSON in code blocks
    code_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
    matches = re.findall(code_block_pattern, text, re.DOTALL)
    for match in matches:
        try:
            result = json.loads(match)
            logger.debug("✅ Successfully extracted JSON from code block")
            return result
        except json.JSONDecodeError:
            continue
    
    # Strategy 4: Find JSON after common prefixes
    prefixes = [
        "json response:",
        "response:",
        "output:",
        "result:",
        "here is the json:",
        "the json is:",
    ]
    
    for prefix in prefixes:
        prefix_pos = text.lower().find(prefix.lower())
        if prefix_pos >= 0:
            remaining_text = text[prefix_pos + len(prefix):].strip()
            extracted = extract_json_from_text(remaining_text)
            if extracted:
                logger.debug(f"✅ Successfully extracted JSON after prefix: {prefix}")
                return extracted
    
    logger.debug("❌ No valid JSON found in text")
    return None


def create_fallback_response(
    text: str, 
    required_fields: Dict[str, Any],
    optional_fields: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Create a fallback response when JSON parsing fails.
    
    Args:
        text: Original LLM response text
        required_fields: Dictionary of required field names and default values
        optional_fields: Dictionary of optional field names and default values
        
    Returns:
        Dictionary with required fields filled
    """
    logger.info(f"🔄 Creating fallback response for text: {text[:50]}...")
    
    fallback = {}
    
    # Fill required fields with defaults or extracted content
    for field_name, default_value in required_fields.items():
        if field_name in ["message", "response_message", "greeting_message"]:
            # Use the original text as the message
            fallback[field_name] = text.strip()
            logger.debug(f"📝 Using text as {field_name}")
        elif field_name in ["agent", "sender_agent", "target_agent"]:
            # Try to extract agent names or use default
            agent_match = re.search(r'agent[:\s]+([a-zA-Z0-9_-]+)', text, re.IGNORECASE)
            if agent_match:
                fallback[field_name] = agent_match.group(1)
                logger.debug(f"🎯 Extracted agent name: {agent_match.group(1)}")
            else:
                fallback[field_name] = default_value or "unknown"
                logger.debug(f"🔧 Using default for {field_name}: {fallback[field_name]}")
        else:
            fallback[field_name] = default_value
            logger.debug(f"⚙️ Setting {field_name} to default: {default_value}")
    
    # Fill optional fields if provided
    if optional_fields:
        for field_name, default_value in optional_fields.items():
            fallback[field_name] = default_value
            logger.debug(f"📋 Adding optional field {field_name}: {default_value}")
    
    logger.info(f"✅ Created fallback response with {len(fallback)} fields")
    return fallback


def robust_json_parse(
    response: Union[str, dict, BaseModel],
    target_model: type,
    required_fields: Dict[str, Any],
    optional_fields: Dict[str, Any] = None
) -> BaseModel:
    """
    Robust JSON parsing with intelligent fallbacks.
    
    Args:
        response: LLM response (string, dict, or Pydantic model)
        target_model: Pydantic model class to create
        required_fields: Required fields with default values
        optional_fields: Optional fields with default values
        
    Returns:
        Instance of target_model
        
    Raises:
        ValueError: If parsing fails completely
    """
    logger.debug(f"🔧 Parsing response of type {type(response).__name__} into {target_model.__name__}")
    
    # If already the target model, return as-is
    if isinstance(response, target_model):
        logger.debug("✅ Response is already target model")
        return response
    
    # If dict, try to create model directly
    if isinstance(response, dict):
        try:
            result = target_model(**response)
            logger.debug("✅ Successfully created model from dict")
            return result
        except Exception as e:
            logger.debug(f"❌ Failed to create model from dict: {e}")
    
    # If string, try JSON extraction
    if isinstance(response, str):
        extracted_json = extract_json_from_text(response)
        
        if extracted_json:
            try:
                result = target_model(**extracted_json)
                logger.debug("✅ Successfully created model from extracted JSON")
                return result
            except Exception as e:
                logger.debug(f"❌ Failed to create model from extracted JSON: {e}")
        
        # Create fallback response
        logger.info("🔄 Creating fallback response for string input")
        fallback_data = create_fallback_response(
            response, 
            required_fields, 
            optional_fields
        )
        
        try:
            result = target_model(**fallback_data)
            logger.info("✅ Successfully created model from fallback data")
            return result
        except Exception as e:
            logger.error(f"❌ Failed to create fallback response: {e}")
            raise ValueError(f"Failed to create fallback response: {e}")
    
    # Unexpected response type
    error_msg = f"Unable to parse response of type {type(response)}: {response}"
    logger.error(f"❌ {error_msg}")
    raise ValueError(error_msg)


def parse_with_fallback(response: Any, model_class: type, **field_defaults) -> BaseModel:
    """
    Convenience function for parsing with automatic field detection.
    
    Args:
        response: LLM response to parse
        model_class: Pydantic model class
        **field_defaults: Default values for fields (field_name=default_value)
        
    Returns:
        Instance of model_class
    """
    # Extract required fields from model
    required_fields = {}
    optional_fields = {}
    
    # Get field info from Pydantic model
    if hasattr(model_class, 'model_fields'):
        for field_name, field_info in model_class.model_fields.items():
            default_value = field_defaults.get(field_name, "")
            
            if field_info.is_required():
                required_fields[field_name] = default_value
            else:
                optional_fields[field_name] = field_info.default
    
    return robust_json_parse(response, model_class, required_fields, optional_fields) 