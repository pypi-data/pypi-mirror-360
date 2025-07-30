from openai import OpenAI as OpenAIClient
from .client import LlumoClient

# Dummy evaluation function that uses LlumoClient
def evaluate_multiple(data, api_key=None,evals=["Response Correctness"]):
    client = LlumoClient(api_key=api_key)
    results= client.evaluateMultiple(data, evals=evals,createExperiment=False,prompt_template="Give answer to the query: {{query}}, using context: {{context}}",getDataFrame=False)
    return results

# Wrapper around ChatCompletion to allow custom fields like `.evaluation`
class ChatCompletionWithEval:
    def __init__(self, response, evaluation):
        self._response = response
        self.evaluation = evaluation

    def __getattr__(self, name):
        return getattr(self._response, name)

    def __getitem__(self, key):
        return self._response[key]

    def __repr__(self):
        return repr(self._response)

class openai(OpenAIClient):
    def __init__(self, api_key: str):
        super().__init__(api_key=api_key)

        original_create = self.chat.completions.create

        class ChatCompletionsWrapper:
            @staticmethod
            def create(*args, **kwargs):
                context = kwargs.pop("context", None)
                evals = kwargs.pop("evals", [])
                llumo_key = kwargs.pop("llumo_key", None)

                messages = kwargs.get("messages", [])
                user_message = next(
                    (m.get("content") for m in reversed(messages) if m.get("role") == "user"),
                    "",
                )

                # If context is None or empty or whitespace-only, set it to user_message
                if not context or context.strip() == "":
                    context = user_message

                response = original_create(*args, **kwargs)

                try:
                    output_text = response.choices[0].message.content
                except Exception:
                    output_text = ""

                eval_input = [{
                    "query": user_message,
                    "context": context,
                    "output": output_text,
                }]

                # Safely call evaluate_multiple, if error return None
                evaluation = None
                try:
                    evaluation = evaluate_multiple(eval_input, api_key=llumo_key,evals=evals)
                except Exception as e:
                    # You can optionally log the error here if you want
                    # print(f"Evaluation failed, skipping: {e}")
                    evaluation = None

                # If evaluation is None, just return normal response
                if evaluation is None:
                    print("Cannot process your request for evaluation, please check your api and try again later.")
                    return response

                # Otherwise wrap with evaluation attached
                return ChatCompletionWithEval(response, evaluation)

        self.chat.completions.create = ChatCompletionsWrapper.create