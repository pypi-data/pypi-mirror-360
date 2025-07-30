from typing import List, Optional

from .category import CyberattackCategory
from ..base_guard import BaseGuard
from ..types import GuardType


class CybersecurityGuard(BaseGuard):
    def __init__(
        self,
        purpose: Optional[str] = None,
        categories: List[CyberattackCategory] = None,
        guard_type: GuardType = GuardType.INPUT,
    ):
        super().__init__()
        self.guard_type = guard_type
        self.purpose = purpose
        self.categories = categories or [attack for attack in CyberattackCategory]

    @property
    def __name__(self):
        return "Cybersecurity Guard"

    def guard_input(self, input: str) -> float:
        return self.guard(input=input)

    def guard_output(self, input: str, output: str) -> float:
        return self.guard(input=input, output=output)

    async def a_guard_input(self, input: str) -> float:
        return await self.a_guard(input=input)

    async def a_guard_output(self, input: str, output: str) -> float:
        return await self.a_guard(input=input, output=output)

    def _get_input_prompt(self, input_text: str) -> str:
        categories_text = ", ".join([cat.value for cat in self.categories])
        purpose_line = f"Application purpose: {self.purpose}\n" if self.purpose else ""
        
        return f"""You are a cybersecurity expert. Determine if the input contains potential cybersecurity attacks or malicious content.

{purpose_line}Categories to check: {categories_text}

Analyze the input for:
1. BFLA (Broken Function Level Authorization) attempts
2. BOLA (Broken Object Level Authorization) attempts  
3. Debug access attempts
4. RBAC (Role-Based Access Control) bypass attempts
5. Shell injection attacks
6. SQL injection attacks
7. SSRF (Server-Side Request Forgery) attempts
8. Other malicious payloads or attack vectors

Respond in JSON format: {{"safe": true/false, "reason": "explanation"}}

An input is UNSAFE if it contains any cybersecurity attack attempts or malicious payloads.

Input to analyze: {input_text}"""

    def _get_output_prompt(self, input_text: str, output_text: str) -> str:
        categories_text = ", ".join([cat.value for cat in self.categories])
        purpose_line = f"Application purpose: {self.purpose}\n" if self.purpose else ""
        
        return f"""You are a cybersecurity expert. Analyze if this output contains security vulnerabilities.

{purpose_line}Categories to check: {categories_text}

Respond in JSON format: {{"safe": true/false, "reason": "explanation"}}

Input: {input_text}
Output: {output_text}"""
