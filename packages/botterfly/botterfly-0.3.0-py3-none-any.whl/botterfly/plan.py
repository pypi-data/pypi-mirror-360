import copy
import hashlib
import json


class Plan:
    def __init__(self, template_renderer, plan_template_str: str, context: dict, result: dict):
        self._template_renderer = template_renderer
        self._plan_template_str = plan_template_str
        self._original_context = context
        self._result = result
        self._last_rendered_plan = []
        self._last_result_hash = None
        self._step_index = 0

    def _hash_result(self) -> str:
        return hashlib.sha256(json.dumps(self._result, sort_keys=True).encode()).hexdigest()

    def _render_plan_if_needed(self):
        current_hash = self._hash_result()
        if current_hash != self._last_result_hash:
            context = copy.deepcopy(self._original_context)
            context.update(self._result)
            self._last_rendered_plan = self._template_renderer.render(
                context, template_str=self._plan_template_str
            )
            self._last_result_hash = current_hash

    def __iter__(self):
        return self

    def __next__(self):
        self._render_plan_if_needed()
        if self._step_index < len(self._last_rendered_plan):
            step = self._last_rendered_plan[self._step_index]
            self._step_index += 1
            return step, self._result
        else:
            raise StopIteration
