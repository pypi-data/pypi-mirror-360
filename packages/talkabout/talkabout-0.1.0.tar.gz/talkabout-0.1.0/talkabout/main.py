from anthropic import Anthropic
import os


class Talk():
    def __init__(self, obj, api_key=None):
        self.obj = obj
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required. Pass it as api_key parameter or set ANTHROPIC_API_KEY environment variable.")
        self.client = Anthropic(api_key=self.api_key)

    def __call__(self, prompt):
        # Get detailed info about the object
        obj_info = self._get_object_info()
        
        full_prompt = f"""You are a Python expert. Given this object with the following detailed information:

{obj_info}

What Python code would access or compute: '{prompt}'?

CRITICAL RULES:
1. Return ONLY a single Python expression that can be evaluated
2. NO explanations, NO markdown, NO backticks, NO comments, NO multi-line code
3. NO text like "Here's how to..." or "You can use..."
4. Just ONE line of raw Python code
5. Use the exact column names, attribute names, and methods shown above
6. ALWAYS use 'obj' as the variable name (NOT ticker, NOT self, NOT anything else)
7. If you're unsure about column names, use the first available column or method

Example valid responses:
obj.quarterly_cashflow.iloc[0, 0].pct_change()
obj.info['marketCap']
obj.history(period='1y')['Close'].mean()

Your response must be ONE LINE of executable Python code ONLY using 'obj' as the variable name."""

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": full_prompt}]
        )
        code = response.content[0].text.strip()
        
        # Remove any markdown formatting that might slip through
        if code.startswith('```python'):
            code = code[9:]
        if code.startswith('```'):
            code = code[3:]
        if code.endswith('```'):
            code = code[:-3]
        code = code.strip()
        
        try:
            print('Executing code:', code)
            print()

            res = eval(code, {"obj": self.obj})
            return res
        except Exception as e:
            return f"❌ Error: {e} for response: {code}"
    
    def _get_object_info(self):
        """Get detailed information about the object's structure and available data."""
        info = []
        
        # Basic object info
        info.append(f"Object type: {type(self.obj).__name__}")
        info.append(f"Object representation: {repr(self.obj)}")
        
        # Get available attributes and methods
        attrs = []
        for attr in dir(self.obj):
            if not attr.startswith('_'):
                try:
                    value = getattr(self.obj, attr)
                    if callable(value):
                        attrs.append(f"  {attr}() - method")
                    else:
                        # For DataFrames, show column info
                        if hasattr(value, 'columns'):
                            cols = list(value.columns)
                            info.append(f"  {attr} - DataFrame with columns: {cols}")
                        elif hasattr(value, 'index'):
                            info.append(f"  {attr} - Series/Index with {len(value)} items")
                        else:
                            info.append(f"  {attr} - {type(value).__name__}")
                except:
                    attrs.append(f"  {attr} - attribute")
        
        if attrs:
            info.append("Available methods:")
            info.extend(attrs)
        
        return "\n".join(info)

