# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------
import json

import pandas as pd
from ibm_watsonx_gov.config import AgenticAIConfiguration, GenAIConfiguration
from ibm_watsonx_gov.entities.evaluation_result import (AggregateMetricResult,
                                                        RecordMetricResult)
from ibm_watsonx_gov.entities.metric import GenAIMetric
from ibm_watsonx_gov.utils.python_utils import (
    get, parse_functions_to_openai_schema)
from llmevalkit.function_calling.pipeline.types import ToolSpec

METRIC_PROMPT_DATA = [
    {"name": "function_intent_alignment", "jsonschema": {"title": "function_intent_alignment", "description": "Assess whether this function call—its name plus all parameter values—correctly implements the user's immediate request as the right next step in the conversation.\n\nKey considerations:\n- The conversation history includes every user request, assistant message, and prior tool call with its output.\n- The user's overall intent may require multiple parallel or chained API calls; here you judge only this one.\n- The tool inventory and API spec define available functions, descriptions, and parameter documentation.\n- Skipping this call should block meaningful progress toward the user's goal, even if further calls follow.\n- Watch for implicit instructions in earlier dialogue (e.g. \"only unread emails\" implies a filter flag).\n- It is valid for this call to run alongside other calls; that does not reduce its correctness.\n\nOn a scale from 1 (irrelevant) to 5 (perfect), rate how precisely this function call—its name and parameter values—matches the user's most recent request and constitutes the correct next step toward fulfilling that request, given the full conversation history, tool inventory, and API specification.", "type": "object", "properties": {"explanation": {"type": "string", "description": "Explain why this call does or does not align with the user's request as the correct next step in the conversation: reference specific user text, tool descriptions, and API spec excerpts."}, "evidence": {"type": "string", "description": "Exact quotes from the conversation history and API specification that support your alignment rating."}, "output": {"type": "integer", "minimum": 1, "maximum": 5, "threshold_low": 3, "threshold_high": 5, "description": "Alignment rating (1=irrelevant, 5=perfect)."}, "confidence": {"type": "number", "minimum": 0, "maximum": 1, "threshold_low": 0.7, "threshold_high": 1, "description": "Confidence in this alignment rating (0.0-1.0)."}, "correction": {"type": "object", "description": "If the alignment is suboptimal, provide a corrected function call JSON snippet suggesting a better name or parameters; otherwise use {}.", "additionalProperties": True}}, "required": [
        "explanation", "evidence", "output", "confidence", "correction"]}, "examples": [{"user_kwargs": {"conversation_context": [{"role": "user", "content": "I need to cancel my order #987."}, {"role": "assistant", "content": "Retrieving order details now."}, {"role": "tool", "name": "get_order_details", "parameters": {"order_id": 987}, "output": {"order_id": 987, "status": "pending"}}, {"role": "assistant", "content": "Got your order details."}], "tools_inventory": [{"name": "get_order_details", "description": "Retrieve order details", "parameters": {"order_id": "integer"}}, {"name": "cancel_order", "description": "Cancels an existing order by its ID", "parameters": {"order_id": "integer"}}], "tool_call": {"name": "cancel_order", "parameters": {"order_id": 987}}}, "output": {"explanation": "The user explicitly asked to \"cancel my order #987,\" and cancel_order(order_id) directly matches that action as the correct next step.", "evidence": "User said \"cancel my order #987\"; API spec: \"cancel_order(order_id) — Cancels an existing order by its ID.\"", "output": 5, "confidence": 0.92, "correction": {}}}, {"user_kwargs": {"conversation_context": [{"role": "user", "content": "I need to cancel my order #987."}, {"role": "assistant", "content": "Here are your orders."}, {"role": "tool", "name": "list_orders", "parameters": {"user_id": 42}, "output": [{"order_id": 123, "status": "shipped"}, {"order_id": 987, "status": "pending"}]}, {"role": "assistant", "content": "Listed orders."}], "tools_inventory": [{"name": "list_orders", "description": "Lists all orders for a user", "parameters": {"user_id": "integer"}}, {"name": "cancel_order", "description": "Cancels an existing order by its ID", "parameters": {"order_id": "integer"}}], "tool_call": {"name": "list_orders", "parameters": {"user_id": 42}}}, "output": {"explanation": "list_orders retrieves all orders but does not cancel any; it fails to enact the user's explicit cancellation request.", "evidence": "User asked \"cancel my order #987\"; list_orders only \"Lists all orders for a user.\"", "output": 1, "confidence": 0.98, "correction": {"name": "cancel_order", "parameters": {"order_id": 987}}}}]},
    {"name": "overall_call_correctness", "jsonschema": {"title": "overall_call_correctness", "description": "Provide a holistic correctness score for this function call by integrating all General Metrics: intent alignment, value grounding, parameter completeness & consistency, prerequisite satisfaction, and sub-goal readiness.\n\nKey considerations (judge independently):\n- Intent Alignment: Does the call implement the user's request as the correct next step?\n- Value Grounding: Are all parameter values non-hallucinated and spec-aligned?\n- Parameter Completeness & Consistency: No implied parameters missing, no contradictions.\n- Prerequisite Satisfaction: Required upstream steps completed successfully.\n- Sub-goal Readiness: The call leaves the conversation poised for subsequent actions.\n", "type": "object", "properties": {"explanation": {"type": "string", "description": "Summarize how each General Metric contributed to your overall score, citing the strongest supporting or conflicting evidence."}, "evidence": {"type": "string", "description": "Quote the most impactful conversation or spec excerpt that influenced your overall score."}, "output": {"type": "number", "minimum": 0, "maximum": 1, "threshold_low": 0.7, "threshold_high": 1, "description": "Overall correctness score (0.00=completely incorrect to 1.00=perfect)."}, "confidence": {"type": "number", "minimum": 0, "maximum": 1, "threshold_low": 0.7, "threshold_high": 1, "description": "Confidence in this overall correctness score (0.0-1.0)."}, "correction": {"type": "object", "description": "If call is incorrect, suggest a JSON snippet for a revised function call.", "additionalProperties": True}}, "required": ["explanation", "evidence", "output", "confidence", "correction"]}, "examples": [
        {"user_kwargs": {"conversation_context": [{"role": "user", "content": "Cancel my order #987."}, {"role": "assistant", "content": "Retrieving order details."}, {"role": "tool", "name": "get_order_details", "parameters": {"order_id": 987}, "output": {"order_id": 987, "status": "pending"}}, {"role": "assistant", "content": "Order is pending; ready to cancel."}], "tools_inventory": [{"name": "get_order_details", "description": "Retrieve order details", "parameters": {"order_id": "integer"}}, {"name": "cancel_order", "description": "Cancels an existing order by its ID", "parameters": {"order_id": "integer"}}], "tool_call": {"name": "cancel_order", "parameters": {"order_id": 987}}}, "output": {"explanation": "Perfect next-step alignment, all values grounded, complete parameters, auth not needed, call sets up subsequent confirmation.", "evidence": "User asked to cancel order #987; spec matches cancel_order(order_id).", "output": 0.97, "confidence": 0.93, "correction": {}}}, {"user_kwargs": {"conversation_context": [{"role": "user", "content": "Get today's date."}], "tools_inventory": [{"name": "get_time", "description": "Retrieve the current local time", "parameters": {"timezone": "string"}}, {"name": "get_date", "description": "Retrieve the current date", "parameters": {}}], "tool_call": {"name": "get_time", "parameters": {"timezone": "UTC"}}}, "output": {"explanation": "Intent misalignment (wrong endpoint), parameters grounded, complete, no prerequisites, but wrong sub-goal.", "evidence": "User asked for date; tool get_time returns time only.", "output": 0.15, "confidence": 0.9, "correction": {"name": "get_date", "parameters": {}}}}]},
    {"name": "prerequisite_satisfaction", "jsonschema": {"title": "prerequisite_satisfaction", "description": "Verify that any upstream steps—authentication, data loading, prior API calls—required by this call have been completed successfully.\n\nKey considerations:\n- Confirm explicit messages such as “Auth token acquired,” “User info loaded,” or “File uploaded successfully.”\n- Respect semantic order implied by the spec (e.g. language detection → translation, image upload → resizing).\n- Detect prerequisite calls that failed or were missing required values.\n- These are examples; other prerequisites may exist depending on the API spec.", "type": "object", "properties": {"explanation": {"type": "string", "description": "Describe which prerequisite steps were required, how you confirmed their completion, or why they are missing."}, "evidence": {"type": "string", "description": "Quote conversation lines showing successful prerequisites or the absence thereof."}, "output": {"type": "integer", "minimum": 0, "maximum": 1, "threshold_low": 1, "threshold_high": 1, "description": "1 if all prerequisites are met; 0 if any are missing or failed."}, "confidence": {"type": "number", "minimum": 0, "maximum": 1, "threshold_low": 0.7, "threshold_high": 1, "description": "Confidence in this prerequisite assessment (0.0-1.0)."}, "correction": {"type": "object", "description": "If prerequisites are missing or failed, provide JSON snippet(s) for the missing or failed prerequisite call(s).", "additionalProperties": True}}, "required": [
        "explanation", "evidence", "output", "confidence", "correction"]}, "examples": [{"user_kwargs": {"conversation_context": [{"role": "assistant", "content": "Auth token acquired for user 42."}], "tools_inventory": [{"name": "get_order_history", "description": "Retrieve past orders", "parameters": {"user_id": "integer"}}], "tool_call": {"name": "get_order_history", "parameters": {"user_id": 42}}}, "output": {"explanation": "Authentication succeeded as confirmed by 'Auth token acquired for user 42.'", "evidence": "Assistant message: 'Auth token acquired for user 42.'", "output": 1, "confidence": 0.95, "correction": {}}}, {"user_kwargs": {"conversation_context": [{"role": "user", "content": "Translate 'Hola' to English."}], "tools_inventory": [{"name": "translate_text", "description": "Translate text to target language", "parameters": {"text": "string", "target": "string"}}, {"name": "detect_language", "description": "Detect the language of the input text", "parameters": {"text": "string"}}], "tool_call": {"name": "translate_text", "parameters": {"text": "Hola", "target": "\"en\""}}}, "output": {"explanation": "Language detection was not performed; source language unknown.", "evidence": "No prior detect_language call in conversation.", "output": 0, "confidence": 0.88, "correction": {"name": "detect_language", "parameters": {"text": "Hola"}}}}]},
    {"name": "parameter_value_grounding", "jsonschema": {"title": "parameter_value_grounding", "description": "Ensure that each parameter's value in the function call is directly supported by the conversation history or the API specification and not invented by the model.\n\nKey considerations:\n- Values must originate from explicit user text, assistant confirmations, prior tool outputs, or documented spec defaults.\n- Optional parameters may default only if the spec defines such a default; otherwise invented defaults are disallowed.\n- Synonyms (e.g. “NYC” → “New York”) are acceptable only if the conversation context already normalized them.\n- Grounding must hold even if this call is one of several sub-goals in a larger multi-call sequence.", "type": "object", "properties": {"explanation": {"type": "string", "description": "Explain why each parameter value is or is not directly grounded in the conversation or spec, citing the specific source of each value."}, "evidence": {"type": "string", "description": "Exact excerpts from user messages, assistant logs, tool outputs, or API spec that justify the grounding judgment."}, "output": {"type": "integer", "minimum": 0, "maximum": 1, "threshold_low": 1, "threshold_high": 1, "description": "1 if all values are grounded; 0 if any value is invented."}, "confidence": {"type": "number", "minimum": 0, "maximum": 1, "threshold_low": 0.7, "threshold_high": 1, "description": "Confidence in this grounding judgment (0.0-1.0)."}, "correction": {"type": "object", "description": "If values are not grounded, provide suggestions for correcting invented values (e.g. ask the user for clarification or use a grounded value from context) as a JSON snippet; otherwise use {}.", "additionalProperties": True}}, "required": [
        "explanation", "evidence", "output", "confidence", "correction"]}, "examples": [{"user_kwargs": {"conversation_context": [{"role": "assistant", "content": "Logged in as user 55; auth token acquired."}, {"role": "assistant", "content": "Ready to fetch your profile."}], "tools_inventory": [{"name": "get_user_profile", "description": "Retrieves a user's profile details", "parameters": {"user_id": "integer"}}], "tool_call": {"name": "get_user_profile", "parameters": {"user_id": 55}}}, "output": {"explanation": "user_id=55 comes directly from the assistant's confirmation 'Logged in as user 55.'", "evidence": "Assistant message: 'Logged in as user 55'", "output": 1, "confidence": 0.95, "correction": {}}}, {"user_kwargs": {"conversation_context": [{"role": "assistant", "content": "Ready to fetch your profile."}], "tools_inventory": [{"name": "get_user_profile", "description": "Retrieves a user's profile details", "parameters": {"user_id": "integer"}}], "tool_call": {"name": "get_user_profile", "parameters": {"user_id": 42}}}, "output": {"explanation": "user_id=42 is not mentioned by the user or assistant and has no spec default; it appears invented.", "evidence": "No prior mention of user_id; spec does not define a default.", "output": 0, "confidence": 0.88, "correction": {"suggestion": "Ask the user or use the authenticated user's ID from context."}}}]},
    {"name": "parameter_completeness_consistency", "jsonschema": {"title": "parameter_completeness_consistency", "description": "Check that the call's parameter set includes all parameters implied by the conversation and that their values do not contradict each other or earlier outputs.\n\nKey considerations:\n- Include any optional parameters implied by user requests (e.g. “only flagged items” implies a filter flag).\n- Ensure value interdependencies hold (e.g., startDate <= endDate, matching unit systems across related fields).\n- Focus on semantic completeness and consistency—do not perform purely syntactic checks for required parameters.\n- Recognize partial values (e.g. a date without time) as less complete if context demands more precision.", "type": "object", "properties": {"explanation": {"type": "string", "description": "Explain which context-implied parameters are present or missing and how parameter values relate semantically without contradictions."}, "evidence": {"type": "string", "description": "Cite conversation lines and tool outputs that imply parameters or relationships among values."}, "output": {"type": "integer", "minimum": 1, "maximum": 5, "threshold_low": 3, "threshold_high": 5, "description": "Completeness/consistency rating (1=incomplete or conflicting; 5=fully complete and consistent)."}, "confidence": {"type": "number", "minimum": 0, "maximum": 1, "threshold_low": 0.7, "threshold_high": 1, "description": "Confidence in this completeness/consistency rating (0.0-1.0)."}, "correction": {
        "type": "object", "description": "If call is incomplete or inconsistent, provide a JSON snippet adding missing optional parameters or correcting relationships; otherwise {}.", "additionalProperties": True}}, "required": ["explanation", "evidence", "output", "confidence", "correction"]}, "examples": [{"user_kwargs": {"conversation_context": [{"role": "user", "content": "Fetch my profile with name and email only."}], "tools_inventory": [{"name": "get_user_profile", "description": "Retrieves user profile", "parameters": {"user_id": "integer", "fields": "list[string]"}}], "tool_call": {"name": "get_user_profile", "parameters": {"user_id": 42, "fields": ["name", "email"]}}}, "output": {"explanation": "Includes both context-implied fields 'name' and 'email'; no contradictions present.", "evidence": "User said 'name and email only'; fields parameter matches exactly.", "output": 5, "confidence": 0.93, "correction": {}}}, {"user_kwargs": {"conversation_context": [{"role": "user", "content": "Fetch my profile with name and email only."}], "tools_inventory": [{"name": "get_user_profile", "description": "Retrieves user profile", "parameters": {"user_id": "integer", "fields": "list[string]"}}], "tool_call": {"name": "get_user_profile", "parameters": {"user_id": 42, "fields": ["name"]}}}, "output": {"explanation": "Missing the context-implied 'email' field; partial date not relevant here.", "evidence": "User requested both 'name and email'; fields only contains 'name'.", "output": 2, "confidence": 0.88, "correction": {"fields": ["name", "email"]}}}]},
    {"name": "function_selection_appropriateness", "jsonschema": {"title": "function_selection_appropriateness", "description": "Judge whether this is the single best function for the user's request at this step, with no more appropriate alternative in the inventory and in general.\n\nKey considerations:\n- Compare against all functions in the tool inventory to ensure no superior match exists.\n- This function should be the primary focus now, even if other calls run in parallel or afterward.\n- Evaluate domain fit, specificity, and granularity relative to the user's immediate goal.\n- The conversation history includes every user request, assistant message, and prior tool call with outputs.\n- The user's overall intent may require multiple parallel or chained API calls; here you judge only this one.\n- Skipping this function should block meaningful progress toward the user's goal at this step.\n", "type": "object", "properties": {"explanation": {"type": "string", "description": "Explain why this function is or is not the optimal choice: reference specific user intent cues, compare to alternative tool descriptions, and justify domain fit and granularity."}, "evidence": {"type": "string", "description": "Exact excerpts from the conversation history or tool inventory (function names/descriptions) that justify the selection judgment."}, "output": {"type": "integer", "minimum": 0, "maximum": 1, "threshold_low": 1, "threshold_high": 1, "description": "Binary indicator of appropriateness: 1 = this is the optimal function choice; 0 = a better alternative exists or this function is inappropriate for the user's request."}, "confidence": {"type": "number", "minimum": 0, "maximum": 1, "threshold_low": 0.7, "threshold_high": 1, "description": "Confidence in this selection judgment (0.00-1.00), reflecting clarity of user intent and availability of alternatives."}, "correction": {"type": "object", "description": "If function selection was inappropriate, provide the JSON snippet with the better alternative function call (name + parameters); if there is no better alternative, use an empty object {}, indicating no correction is needed. In case of no alternative existing and the function is not appropriate, write json with the suggestion for the function call or for the user to provide more information.", "additionalProperties": True}}, "required": [
        "explanation", "evidence", "output", "confidence", "correction"]}, "examples": [{"user_kwargs": {"conversation_context": [{"role": "user", "content": "What's the weather in New York today?"}], "tools_inventory": [{"name": "get_weather", "description": "Retrieve weather forecast for a location", "parameters": {"location": "string"}}, {"name": "get_time", "description": "Retrieve current local time", "parameters": {"timezone": "string"}}], "tool_call": {"name": "get_weather", "parameters": {"location": "New York"}}, "function_name": "get_weather"}, "output": {"explanation": "get_weather directly returns weather data for a location; no other tool provides forecast information.", "evidence": "User asked for weather; only get_weather in inventory covers weather forecasts.", "output": 1, "confidence": 0.95, "correction": {}}}, {"user_kwargs": {"conversation_context": [{"role": "user", "content": "What time is it in Tokyo?"}], "tools_inventory": [{"name": "translate_text", "description": "Translate text to a target language", "parameters": {"text": "string", "target_language": "string"}}, {"name": "get_time", "description": "Retrieve current local time", "parameters": {"timezone": "string"}}], "tool_call": {"name": "translate_text", "parameters": {"text": "Hello", "target_language": "en"}}, "function_name": "translate_text"}, "output": {"explanation": "translate_text performs translation, not time retrieval; it does not address the user's request for current time.", "evidence": "User asked for time in Tokyo; translate_text does not provide time data.", "output": 0, "confidence": 0.9, "correction": {"name": "get_time", "parameters": {"timezone": "Tokyo"}}}}]},
    {"name": "value_format_alignment", "jsonschema": {"title": "value_format_alignment", "description": "Check that the parameter's value exactly conforms to the API specification's required type, format, and unit conventions for this call.\n\nKey considerations:\n- Data types: string vs. integer, enumeration values, regex or pattern requirements.\n- Formats: ISO dates (e.g. YYYY-MM-DD), timestamp layouts (e.g. RFC3339), currency notation (e.g. USD 100.00).\n- Units: presence or absence of unit suffix (e.g. “seconds” vs. “s”) only if the spec mandates explicit units.\n- Consistency across related parameters (e.g. both start and end timestamps use the same timezone).\n- Do not infer missing units; the value must match spec exactly.\n\nOutput 1 if the value of parameter “<parameter_name>” fully complies with the spec's type, format, and unit rules; otherwise 0.", "type": "object", "properties": {"explanation": {"type": "string", "description": "Explain precisely why the parameter value does or does not match the spec's type, format, and unit requirements, citing the relevant spec excerpt and value format."}, "evidence": {"type": "string", "description": "Quote the spec's type/format definition and the actual provided value that supports your judgment."}, "output": {"type": "integer", "minimum": 0, "maximum": 1, "threshold_low": 1, "threshold_high": 1, "description": "1 if the value conforms exactly; 0 otherwise."}, "confidence": {"type": "number", "minimum": 0, "maximum": 1, "threshold_low": 0.7, "threshold_high": 1, "description": "Confidence in this format alignment judgment (0.0-1.0)."}, "correction": {
        "type": "object", "description": "If the value format is incorrect, provide a JSON snippet showing the corrected value with proper type, format, and unit; otherwise use {}.", "additionalProperties": True}}, "required": ["explanation", "evidence", "output", "confidence", "correction"]}, "examples": [{"user_kwargs": {"conversation_context": [{"role": "user", "content": "Start a countdown for 5 minutes."}], "tools_inventory": [{"name": "set_timer", "description": "Set a countdown timer", "parameters": {"duration": "string"}}], "tool_call": {"name": "set_timer", "parameters": {"duration": "5 minutes"}}, "parameter_name": "duration", "parameter_value": "5 minutes"}, "output": {"explanation": "The spec requires a string with unit (e.g. “5 minutes”); provided value matches exactly.", "evidence": "Spec: duration:string (e.g. “5 minutes\"); provided “5 minutes”.", "output": 1, "confidence": 0.94, "correction": {}}}, {"user_kwargs": {"conversation_context": [{"role": "user", "content": "Start a countdown for 5 minutes."}], "tools_inventory": [{"name": "set_timer", "description": "Set a countdown timer", "parameters": {"duration": "string"}}], "tool_call": {"name": "set_timer", "parameters": {"duration": "300000"}}, "parameter_name": "duration", "parameter_value": "300000"}, "output": {"explanation": "Provided as number of milliseconds without unit, but spec requires a string including unit.", "evidence": "Spec: duration:string (e.g. “5 minutes\"); provided “300000”.", "output": 0, "confidence": 0.93, "correction": {"duration": "\"5 minutes\""}}}]},
    {"name": "parameter_info_sufficiency", "jsonschema": {"title": "parameter_info_sufficiency", "description": "Determine if the provided parameter value is sufficiently detailed and unambiguous, or if additional user detail is required.\n\nKey considerations:\n- Ambiguous numeric values (“5”) without units (“minutes” vs. “seconds”).\n- Partial information: date without time when time is required, time without timezone when multiple zones apply.\n- Nested objects: ensure all required subfields are present (e.g. address:{street,city,state}).\n- Deprecated shorthand allowed only if spec explicitly permits it.\n- User context: values implied earlier may fill gaps but only if clearly stated.\n\nOutput 1 if the value is sufficiently detailed and unambiguous given the conversation context and API spec; otherwise 0.", "type": "object", "properties": {"explanation": {"type": "string", "description": "Describe why the value is or isn't sufficiently detailed, referencing ambiguity or missing details, and what additional information might be needed."}, "evidence": {"type": "string", "description": "Quote the conversation context or spec requirements that highlight the ambiguity or sufficiency of the value."}, "output": {"type": "integer", "minimum": 0, "maximum": 1, "threshold_low": 1, "threshold_high": 1, "description": "1 if the value is unambiguous and complete; 0 if more detail is required."}, "confidence": {"type": "number", "minimum": 0, "maximum": 1, "threshold_low": 0.7, "threshold_high": 1, "description": "Confidence in this sufficiency judgment (0.0-1.0)."}, "correction": {
        "type": "object", "description": "If this value is not sufficiently detailed, suggest a follow-up question or a JSON stub requesting the missing detail; otherwise use {}.", "additionalProperties": True}}, "required": ["explanation", "evidence", "output", "confidence", "correction"]}, "examples": [{"user_kwargs": {"conversation_context": [{"role": "user", "content": "Set an alarm for 07:30 AM tomorrow."}], "tools_inventory": [{"name": "set_alarm", "description": "Set an alarm", "parameters": {"time": "string"}}], "tool_call": {"name": "set_alarm", "parameters": {"time": "07:30 AM"}}, "parameter_name": "time", "parameter_value": "07:30 AM"}, "output": {"explanation": "Time includes hours, minutes, and AM/PM; matches user's unambiguous instruction.", "evidence": "User said “07:30 AM tomorrow”; value “07:30 AM” covers time precisely.", "output": 1, "confidence": 0.93, "correction": {}}}, {"user_kwargs": {"conversation_context": [{"role": "user", "content": "Set an alarm for 7."}], "tools_inventory": [{"name": "set_alarm", "description": "Set an alarm", "parameters": {"time": "string"}}], "tool_call": {"name": "set_alarm", "parameters": {"time": "7"}}, "parameter_name": "time", "parameter_value": "7"}, "output": {"explanation": "Value “7” lacks AM/PM or specific format, making it ambiguous.", "evidence": "User said “7” with no further context; spec expects full time string.", "output": 0, "confidence": 0.94, "correction": {"suggestion": "Ask: “Do you mean 7:00 AM or 7:00 PM?\""}}}]},
    {"name": "parameter_hallucination_check", "jsonschema": {"title": "parameter_hallucination_check", "description": "Ensure the parameter's value is not hallucinated but grounded in the dialogue context or the API spec.\n\nKey considerations:\n- No arbitrary IDs, timestamps, or settings invented without user or spec support.\n- Accept spec-documented defaults only if explicitly listed.\n- Reject values that match neither user utterances nor spec examples.\n\nOutput 1 if the value is fully grounded; otherwise 0.", "type": "object", "properties": {"explanation": {"type": "string", "description": "Explain why the parameter value is or isn't grounded in user/spec context, pointing to the exact source or noting absence."}, "evidence": {"type": "string", "description": "Quote user messages, assistant logs, prior tool outputs, or spec excerpts that support grounding or reveal hallucination."}, "output": {"type": "integer", "minimum": 0, "maximum": 1, "threshold_low": 1, "threshold_high": 1, "description": "1 if grounded; 0 if hallucinated."}, "confidence": {"type": "number", "minimum": 0, "maximum": 1, "threshold_low": 0.7, "threshold_high": 1, "description": "Confidence in this hallucination assessment (0.0-1.0)."}, "correction": {"type": "object", "description": "If value is not grounded, provide a JSON snippet with the corrected value or follow-up action to obtain it; otherwise use {}.", "additionalProperties": True}}, "required": [
        "explanation", "evidence", "output", "confidence", "correction"]}, "examples": [{"user_kwargs": {"conversation_context": [{"role": "user", "content": "Translate 'hello' to Spanish."}], "tools_inventory": [{"name": "translate_text", "description": "Translate given text", "parameters": {"text": "string", "target_lang": "string"}}], "tool_call": {"name": "translate_text", "parameters": {"text": "hello", "target_lang": "es"}}, "parameter_name": "target_lang", "parameter_value": "es"}, "output": {"explanation": "target_lang='es' comes directly from request “to Spanish” and matches spec's ISO code requirement.", "evidence": "User said “to Spanish”; spec uses ISO codes.", "output": 1, "confidence": 0.96, "correction": {}}}, {"user_kwargs": {"conversation_context": [{"role": "user", "content": "Fetch my latest tweets."}], "tools_inventory": [{"name": "get_tweets", "description": "Retrieve recent tweets", "parameters": {"username": "string", "count": "integer"}}], "tool_call": {"name": "get_tweets", "parameters": {"username": "elonmusk", "count": 20}}, "parameter_name": "count", "parameter_value": 20}, "output": {"explanation": "count=20 is invented; user did not specify number of tweets.", "evidence": "No user mention of tweet count; spec default is 10.", "output": 0, "confidence": 0.88, "correction": {"count": 10}}}]},
    {"name": "overall_parameter_correctness", "jsonschema": {"title": "overall_parameter_correctness", "description": "Give a final binary judgment: is this parameter's value correct—grounded, well-formatted, sufficient, consistent, and non-hallucinated? Consider other parameter values and the conversation context.\n\nKey considerations:\n- Integrates grounding, format alignment, information sufficiency, importance, hallucination check, and consistency with other parameters.\n- Considers the entire conversation history, tool inventory, and all parameter values in this call.\n\nOutput 1 if the parameter value is correct in all respects; otherwise 0.", "type": "object", "properties": {"explanation": {"type": "string", "description": "Summarize why this parameter's value is correct or incorrect, referencing any failures in grounding, formatting, sufficiency, importance, or consistency."}, "evidence": {"type": "string", "description": "Quote the most impactful evidence from the conversation, tool outputs, or spec that supports your judgment."}, "output": {"type": "integer", "minimum": 0, "maximum": 1, "threshold_low": 1, "threshold_high": 1, "description": "1 if the parameter is fully correct; 0 if any aspect fails."}, "confidence": {"type": "number", "minimum": 0, "maximum": 1, "threshold_low": 0.7, "threshold_high": 1,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  "description": "Confidence in this overall parameter correctness judgment (0.0-1.0)."}, "correction": {"type": "object", "description": "If the value is not correct, provide a JSON snippet with the corrected parameter value or follow-up action.", "additionalProperties": True}}, "required": ["explanation", "evidence", "output", "confidence", "correction"]}, "examples": [{"user_kwargs": {"conversation_context": [{"role": "user", "content": "Translate 'good night' to German."}], "tools_inventory": [{"name": "translate_text", "description": "Translate text", "parameters": {"text": "string", "target_lang": "string"}}], "tool_call": {"name": "translate_text", "parameters": {"text": "good night", "target_lang": "de"}}, "parameter_name": "target_lang", "parameter_value": "de"}, "output": {"explanation": "Value is grounded (user requested German), format matches ISO codes, sufficient, essential, not hallucinated.", "evidence": "User said “to German”; spec uses ISO codes.", "output": 1, "confidence": 0.97, "correction": {}}}, {"user_kwargs": {"conversation_context": [{"role": "user", "content": "Translate 'good night' to German."}], "tools_inventory": [{"name": "translate_text", "description": "Translate text", "parameters": {"text": "string", "target_lang": "string"}}], "tool_call": {"name": "translate_text", "parameters": {"text": "good night", "target_lang": "es"}}, "parameter_name": "target_lang", "parameter_value": "es"}, "output": {"explanation": "Parameter value 'es' contradicts user intent to translate into German and is not grounded.", "evidence": "User said “to German”; provided 'es' (Spanish).", "output": 0, "confidence": 0.95, "correction": {"target_lang": "de"}}}]}

]


class ToolCallMetricProvider():
    """
    Base class for Tool Call Metrics Computation.
    """

    def pre_process(self, data: pd.DataFrame, configuration: GenAIConfiguration | AgenticAIConfiguration):
        """
        Preprocess the dataframe and tool list for metrics computation

        Args:
            data (pd.DataFrame): Input dataframe

        Returns:
            pd.Dataframe: Processed dataframe
        """
        # Get the specification of tools used in the application
        # in proper format if it is a list of Callable
        if isinstance(configuration.tools, list) and all(callable(item) for item in configuration.tools):
            configuration.tools = self.get_tools_list_schema(
                configuration.tools)

        # TODO: Add validation for the tool_call_field data schema
        tool_call_field = configuration.tool_calls_field
        if tool_call_field:
            data[tool_call_field] = data[tool_call_field].apply(
                lambda x: json.loads(x) if isinstance(x, str) else x)
        return data

    @staticmethod
    def get_tools_list_schema(tools: list) -> list:
        """
        Convert the list of callable objects to the
        format needed for the TCH computation

        Args:
            tools (list): List of Callable objects

        Returns:
            list: List of dictionary containing the tool
            specifications
        """
        tools_specifications = []
        for func in tools:
            tool_schema = parse_functions_to_openai_schema(func)
            if not tool_schema:
                continue
            tools_specifications.append(ToolSpec.model_validate(tool_schema))

        return tools_specifications

    def extract_tool_calls_from_response(self, tool_calls_response) -> list:
        """
        Extracts the tool calls from the response

        Args:
            tool_calls_response (Any): The tool calls response
            can be a list of dictionary, an AIMessage object
            or a dictionary

        Returns:
            list: List of openai formatted tool call
        """
        if isinstance(tool_calls_response, dict):
            tool_calls = get(tool_calls_response, "kwargs.tool_calls")
        elif hasattr(tool_calls_response, "tool_calls"):
            tool_calls = tool_calls_response.tool_calls
        else:
            tool_calls = tool_calls_response
        converted = []
        for call in tool_calls:
            converted.append({
                "id": call["id"],
                "type": "function",
                "function": {
                    "name": call["name"],
                    "arguments": json.dumps(call["args"])
                }
            })
        return converted

    def post_process(self, results: pd.DataFrame, configuration: GenAIConfiguration | AgenticAIConfiguration, metric: GenAIMetric):
        """
        Post process the computed metrics to get the Aggregated Result and
        Record level metric result in the proper format

        Args:
            results (pd.DataFrame): Computed metric results
            configuration (GenAIConfiguration | AgenticAIConfiguration): Metric configuration

        Returns:
            AggregateMetricResult: The AggregateMetricResult object containing the calculated
            metrics information
        """

        # Preparing the record level metrics
        record_level_metrics: list[RecordMetricResult] = []

        for row in results:
            record_level_metrics.append(
                RecordMetricResult(
                    name=metric.name,
                    method=metric.method,
                    value=row.get("value"),
                    provider="ibm",
                    group=metric.group,
                    record_id=row["record_id"],
                    thresholds=metric.thresholds,
                    additional_info={"explanations": row.get("explanations")}
                )
            )

        # Get the number of records are violated, min, max
        values = [item.get("value", 0.0) for item in results]
        count_invalid = sum(val == 1.0 for val in values)
        min_value = min(values, default=0.0)
        max_value = max(values, default=0.0)
        value = int(count_invalid)/int(len(results))

        # creating AggregateMetricResult
        aggregated_result = AggregateMetricResult(
            name=metric.name,
            method=metric.method,
            provider="ibm",
            group=metric.group,
            value=value,
            total_records=len(results),
            record_level_metrics=record_level_metrics,
            min=min_value,
            max=max_value,
            thresholds=metric.thresholds
        )

        # return the aggregated result
        return aggregated_result

    def get_semantic_metric_json(self, name):
        """
        Returns the first dictionary with matching 'name' or None if not found.

        Args:
            name (str): semantic evaluator metric name
        """

        return next((item for item in METRIC_PROMPT_DATA if item.get("name") == name), None)

    def get_llm_metric_client(self, llm_judge):
        """
        Based on the llm_judge return the
        metrics client for semantic metrics
        """
        from llmevalkit.llm import get_llm

        if llm_judge.get_model_provider() == "ibm_watsonx.ai":
            MetricsClientCls = get_llm("litellm.watsonx.output_val")
        elif llm_judge.get_model_provider() == "openai":
            MetricsClientCls = get_llm("openai.async")

        metrics_client = MetricsClientCls(
            model_name=llm_judge.model.model_id)

        return metrics_client

    def extract_parameter_info(self, data, metric_mapping_name):
        """
        Extract parameter metrics into a list

        Args:
            data (dict): Response data to be extracted
            metric_mapping_name (str): Metric mapping name

        Returns:
            List: List of Parameter based explanation
        """
        result = {
            "is_issue": False,
            "raw_response": []
        }

        for param_name, param_data in data.get("parameter", {}).items():
            metrics = get(param_data, f"metrics.{metric_mapping_name}")
            raw_response = metrics['raw_response']
            is_issue = metrics.get('is_issue', False)

            if is_issue:
                result["is_issue"] = True

            param_info = {
                "parameter": param_name,
                "explanation": raw_response['explanation'],
                "evidence": raw_response['evidence'],
                "output": raw_response['output'],
                "confidence": raw_response['confidence'],
                "correction": raw_response['correction'],
                "is_issue": is_issue
            }

            result["raw_response"].append(param_info)

        return result
