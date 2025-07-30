from typing import List, Dict, Any
import time
import asyncio

from deepteam.guardrails.base_guard import BaseGuard
from deepteam.guardrails.types import GuardType


class GuardResult:
    def __init__(self, guard_results: Dict[str, Any]):
        self.guard_results = guard_results
        # Calculate breached automatically from guard results
        self.breached = any(
            not result.get("safe", False) 
            for result in guard_results.values()
        )


class Guardrails:
    """
    Open-source guardrails system for production LLM safety.
    Fast binary classification to guard inputs and outputs.
    """
    
    def __init__(self, guards: List[BaseGuard]):
        self.guards: List[BaseGuard] = guards

    def guard_input(self, input: str) -> GuardResult:
        """
        Guard an input string using all configured guards.
        Returns GuardResult with binary safe/unsafe classification.
        """
        if len(self.guards) == 0:
            raise TypeError(
                "Guardrails cannot guard inputs when no guards are provided."
            )

        guard_results = {}
        
        for guard in self.guards:
            start_time = time.time()
            try:
                is_safe = guard.guard_input(input)
                latency = time.time() - start_time
                
                guard_results[guard.__name__] = {
                    "safe": is_safe,
                    "latency": latency,
                    "reason": getattr(guard, "reason", None),
                    "score": getattr(guard, "score", None)
                }
                    
            except Exception as e:
                guard_results[guard.__name__] = {
                    "safe": False,
                    "latency": time.time() - start_time,
                    "error": str(e)
                }

        return GuardResult(guard_results=guard_results)

    def guard_output(self, input: str, output: str) -> GuardResult:
        """
        Guard an output string using all configured guards.
        Returns GuardResult with binary safe/unsafe classification.
        """
        if len(self.guards) == 0:
            raise TypeError(
                "Guardrails cannot guard outputs when no guards are provided."
            )

        guard_results = {}
        
        for guard in self.guards:
            start_time = time.time()
            try:
                is_safe = guard.guard_output(input, output)
                latency = time.time() - start_time
                
                guard_results[guard.__name__] = {
                    "safe": is_safe,
                    "latency": latency,
                    "reason": getattr(guard, "reason", None),
                    "score": getattr(guard, "score", None)
                }
                    
            except Exception as e:
                guard_results[guard.__name__] = {
                    "safe": False,
                    "latency": time.time() - start_time,
                    "error": str(e)
                }

        return GuardResult(guard_results=guard_results)

    async def a_guard_input(self, input: str) -> GuardResult:
        """
        Async version of guard_input for better performance.
        """
        if len(self.guards) == 0:
            raise TypeError(
                "Guardrails cannot guard inputs when no guards are provided."
            )

        tasks = []
        for guard in self.guards:
            task = asyncio.create_task(self._async_guard_input_single(guard, input))
            tasks.append((guard, task))

        guard_results = {}

        for guard, task in tasks:
            try:
                result = await task
                guard_results[guard.__name__] = result
            except Exception as e:
                guard_results[guard.__name__] = {
                    "safe": False,
                    "error": str(e)
                }

        return GuardResult(guard_results=guard_results)

    async def a_guard_output(self, input: str, output: str) -> GuardResult:
        """
        Async version of guard_output for better performance.
        """
        if len(self.guards) == 0:
            raise TypeError(
                "Guardrails cannot guard outputs when no guards are provided."
            )

        tasks = []
        for guard in self.guards:
            task = asyncio.create_task(self._async_guard_output_single(guard, input, output))
            tasks.append((guard, task))

        guard_results = {}

        for guard, task in tasks:
            try:
                result = await task
                guard_results[guard.__name__] = result
            except Exception as e:
                guard_results[guard.__name__] = {
                    "safe": False,
                    "error": str(e)
                }

        return GuardResult(guard_results=guard_results)

    async def _async_guard_input_single(self, guard: BaseGuard, input: str):
        """Helper method for async input guarding."""
        start_time = time.time()
        is_safe = await guard.a_guard_input(input)
        latency = time.time() - start_time
        
        return {
            "safe": is_safe,
            "latency": latency,
            "reason": getattr(guard, "reason", None),
            "score": getattr(guard, "score", None)
        }

    async def _async_guard_output_single(self, guard: BaseGuard, input: str, output: str):
        """Helper method for async output guarding."""
        start_time = time.time()
        is_safe = await guard.a_guard_output(input, output)
        latency = time.time() - start_time
        
        return {
            "safe": is_safe,
            "latency": latency,
            "reason": getattr(guard, "reason", None),
            "score": getattr(guard, "score", None)
        }
