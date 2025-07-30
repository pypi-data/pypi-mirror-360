import asyncio
import os
import re
import subprocess
import tempfile
from typing import Any, Dict

import constants
import streamlit as st
from llm_provider import *


class CSPExtractor:

    @staticmethod
    def extract_pycsp3_code(text: str) -> str:
        # Pattern to match PyCSP3 code blocks
        patterns = [
            r"```python\s*(.*?)```",
            r"```\s*(.*?)```",
            r"from pycsp3.*?(?=\n\n|\Z)",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                if "pycsp3" in match.lower() or "csp" in match.lower():
                    return match.strip()

        # If no code block found, try to extract lines containing CSP keywords
        lines = text.split("\n")
        csp_lines = []
        in_code = False

        for line in lines:
            if any(
                keyword in line.lower()
                for keyword in [
                    "import pycsp3",
                    "from pycsp3",
                    "Variable",
                    "Domain",
                    "satisfy",
                ]
            ):
                in_code = True
            if in_code:
                csp_lines.append(line)
            if line.strip() == "" and in_code and len(csp_lines) > 5:
                break

        return "\n".join(csp_lines) if csp_lines else text


class MCPCSPRunner:

    def __init__(self):
        self.session = None

    async def initialize_mcp(self):
        try:
            # This would typically connect to an MCP server
            # For demo purposes, we'll simulate the MCP environment
            self.session = "mock_session"  # Replace with actual MCP session
            return True
        except Exception as e:
            st.error(f"Failed to initialize MCP: {e}")
            return False

    async def run_csp_code(self, code: str) -> Dict[str, Any]:
        try:
            # Create temporary file with the CSP code
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                # Add necessary imports if not present
                if "from pycsp3" not in code and "import pycsp3" not in code:
                    code = "from pycsp3 import *\n" + code

                # Ensure the code ends with solve() if not present
                if "solve()" not in code:
                    code += "\n\nresult = solve()\nprint(f'Solution: {result}')"

                f.write(code)
                temp_file = f.name

            try:
                result = subprocess.run(
                    ["python", temp_file], capture_output=True, text=True, timeout=30
                )

                return {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr,
                    "code": code,
                }
            finally:
                # Clean up temporary file
                os.unlink(temp_file)

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "Code execution timed out",
                "code": code,
            }
        except Exception as e:
            return {"success": False, "output": "", "error": str(e), "code": code}


class CSPGenerator:

    def __init__(self, model: str, brand: str) -> None:

        self.brand = brand
        self.model = model
        self.client_provider: ClientBrand
        if self.brand == constants.ANTHROPIC_PREFIX:
            self.client_provider = ClientAnthopicBrand()
        elif self.brand == constants.CRIL_PREFIX:
            self.client_provider = ClientCrilBrand()
        elif self.brand == constants.GOOGLE_PREFIX:
            self.client_provider = ClientGoogleBrand()
        else:
            self.client_provider = ClientGPTBrand()

        self.client = self.client_provider.get_client()
        print(
            "*" * 50,
            self.brand,
            self.model,
            self.client_provider,
            self.client_provider.get_error_messages(),
        )

    def get_error_messages(self):
        return self.client_provider.get_error_messages()

    async def generate_csp_code_stream_async(
        self, problem_description: str, response_container
    ):
        if self.brand == constants.ANTHROPIC_PREFIX:
            return await self.generate_csp_code_stream_async_claude(
                problem_description, response_container
            )
        elif self.brand == constants.CRIL_PREFIX:
            return await self.generate_csp_code_stream_async_openai(
                problem_description, response_container
            )
        else:
            return await self.generate_csp_code_stream_async_openai(
                problem_description, response_container
            )

    async def generate_csp_code_stream_async_claude(
        self, problem_description: str, response_container
    ):
        """Generate PyCSP3 code using LLM with async streaming"""
        prompt = f"""You are an assistant specializing in solving constraint problems. 
        You are able to generate PyCSP3 code to solve the following constraint programming problem:
        
        {problem_description}
        
        Requirements:
        1. Use PyCSP3 syntax (from pycsp3 import *)
        2. Define variables with appropriate domains
        3. Add all necessary constraints
        4. Include solve() call
        5. Print the solution clearly
        6. Make the code executable and complete
        
        Provide only the Python code with PyCSP3, no explanations.
        """

        try:
            full_response = ""

            # Create async streaming response
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=st.session_state.max_tokens,
                temperature=st.session_state.temperature,
                messages=[{"role": "user", "content": prompt}],
            ) as stream:

                # Initialize the response container
                response_placeholder = response_container.empty()

                async for chunk in stream:
                    # print(chunk)
                    if chunk.type == "content_block_delta":
                        if hasattr(chunk.delta, "text"):
                            full_response += chunk.delta.text
                            # Update the display in real-time
                            response_placeholder.code(full_response, language="python")
                    elif chunk.type == "message_delta":
                        # Handle any message-level updates if needed
                        pass

            return full_response

        except Exception as e:
            error_msg = f"Error generating code: {str(e)}"
            response_container.error(error_msg)
            return error_msg

    async def generate_csp_code_stream_async_openai(
        self, problem_description: str, response_container
    ):
        """Generate PyCSP3 code using LLM with async streaming"""
        prompt = f"""You are an assistant specializing in solving constraint problems. 
        You are able to generate PyCSP3 code to solve the following constraint programming problem:
        
        {problem_description}
        
        Requirements:
        1. Use PyCSP3 syntax (from pycsp3 import *)
        2. Define variables with appropriate domains
        3. Add all necessary constraints
        4. Include solve() call
        5. Print the solution clearly
        6. Make the code executable and complete
        
        Provide only the Python code with PyCSP3, no explanations.
        """

        full_response = ""

        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=st.session_state.temperature,
                max_tokens=st.session_state.max_tokens,
                stream=True,
            )

            response_placeholder = response_container.empty()

            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    # yield chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)
            return full_response
        except Exception as e:
            return f"\n❌ Error: {str(e)}"

    def generate_csp_code_stream(self, problem_description: str, response_container):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.generate_csp_code_stream_async(
                    problem_description, response_container
                )
            )
        finally:
            loop.close()
