# Vaidya AI First Inference Error - Fixed

## Problem Summary
The system was returning **malformed JSON with "Unknown" dosha on the first query**, but working correctly on subsequent queries. This was a **model warm-up and response parsing issue**.

## Root Causes Identified
1. **Cold Start Issue**: llama-server wasn't fully warmed up on first request, causing incomplete/malformed responses
2. **No Health Check**: System tried to query before server was ready
3. **Weak JSON Parsing**: Regex couldn't handle unquoted arrays with parentheses like `[Ginger (1g), Warm water (200ml)]`
4. **No Response Validation**: Accepted empty or truncated responses without validation

## Solutions Implemented

### 1. Server Warm-up System (llm_inference.py)
```python
Added _warm_up_server() method that:
- Sends a dummy request on first use to load the model
- Waits for server to be ready with exponential backoff
- Validates server is responding before proceeding
```

### 2. Improved Health Checks
```python
Added _is_server_ready() method to:
- Check server health before queries
- Time out quickly if server is down
- Wait with exponential backoff (0.5s → 5s max)
```

### 3. Enhanced JSON Parsing (main.py)
```python
New _fix_malformed_json() function that:
- Intelligently fixes unquoted array items with parentheses
- Respects existing quote formatting
- Handles partial/truncated JSON by completing braces
- Gracefully degrades on failure
```

### 4. Response Validation
```python
Updated _query_server() to:
- Validate response length (minimum 10 chars meaningful content)
- Log debug info for failures
- Better error messages for troubleshooting
```

## System Prompt Improvement
Updated to explicitly instruct model to use JSON list format:
```
"natural_remedies/lifestyle/dietary must be arrays of short strings 
with proper JSON list format ["item1", "item2"]"
```

## Files Modified
1. **c:\idea1\vaidya_slm\backend\ai\llm_inference.py**
   - Added `time` import
   - Added `_is_server_ready()` method
   - Added `_wait_for_server_ready()` method
   - Added `_warm_up_server()` method
   - Updated `_query_server()` with warm-up and validation

2. **c:\idea1\vaidya_slm\backend\main.py**
   - Added `Optional` to imports
   - Added `_fix_malformed_json()` helper function
   - Updated `_extract_model_sections()` to use improved parsing

## Testing
Run this to verify the fixes:
```bash
cd c:\idea1
python test_first_inference.py
```

The test validates:
- JSON parsing of malformed responses ✓
- Array item unquoting with parentheses ✓
- Truncated JSON completion ✓
- Server health check ✓

## Expected Behavior Now
1. **First Request**: System sends warm-up query, loads model into cache
2. **Actual Request**: Model is fully ready, returns properly formatted JSON
3. **Response Parsing**: All malformed JSON variants are handled gracefully
4. **Output**: Correct dosha detection (Pitta, Vata, Kapha, etc.) on FIRST attempt

## How to Verify
Test with these symptoms in sequence:
1. "stomach pain" → Should return Pitta with high confidence
2. "nausea and fatigue" → Should return appropriate dosha
3. "joint stiffness" → Should return Vata imbalance

All should work correctly on **first click** without needing to retry.

## Additional Benefits
- Better error logging for debugging
- More robust to varied LLM output formats
- Handles partial/streaming responses
- Exponential backoff prevents CPU spinning
- Warm-up model only once per backend restart
