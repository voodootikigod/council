import unittest
from typing import List

from council.evaluators import LLMEvaluator
from council.contexts import (
    AgentContext,
    ChatHistory,
    ScoredChatMessage,
    ChatMessage,
)
from council.mocks import MockLLM
from council.runners import Budget


class TestLLMEvaluator(unittest.TestCase):
    def setUp(self) -> None:
        self.context = AgentContext(ChatHistory())
        self.context.chatHistory.add_user_message("bla")

    def add_one_iteration_result(self):
        self.first_context = self.context.new_chain_context("a chain")
        self.second_context = self.context.new_chain_context("another chain")
        self.first_context.current.append(ChatMessage.skill("result of a chain", source="first skill"))
        self.second_context.current.append(ChatMessage.skill("result of another chain", source="another skill"))

    @staticmethod
    def to_tuple_message_score(items: List[ScoredChatMessage]):
        return [(item.message.message, item.score) for item in items]

    def test_evaluate(self):
        responses = ["result of a chain:2", "result of another chain:10"]
        expected = [
            ScoredChatMessage(ChatMessage.agent("result of a chain"), 2),
            ScoredChatMessage(ChatMessage.agent("result of another chain"), 10),
        ]

        self.add_one_iteration_result()

        result = LLMEvaluator(MockLLM.from_multi_line_response(responses)).execute(self.context, Budget(10))
        self.assertEqual(self.to_tuple_message_score(expected), self.to_tuple_message_score(result))

    def test_evaluate_chain_with_no_message(self):
        responses = ["result of a chain:2", "result of another chain:10"]
        expected = [
            ScoredChatMessage(ChatMessage.agent("result of a chain"), 2),
            ScoredChatMessage(ChatMessage.agent("result of another chain"), 10),
        ]

        self.add_one_iteration_result()
        self.context.new_chain_context("this chain does not provide any message")

        result = LLMEvaluator(MockLLM.from_multi_line_response(responses)).execute(self.context, Budget(10))
        self.assertEqual(self.to_tuple_message_score(expected), self.to_tuple_message_score(result))

    def test_evaluate_fail_to_parse(self):
        response = "a response with no score"
        instance = LLMEvaluator(MockLLM.from_response(response))
        self.add_one_iteration_result()
        with self.assertRaises(Exception):
            instance.execute(self.context, Budget(10))

    def test_evaluate_with_execution_history(self):
        responses = ["result of a chain:2", "result of another chain:10"]
        expected = [
            ScoredChatMessage(ChatMessage.agent("result of a chain"), 2),
            ScoredChatMessage(ChatMessage.agent("result of another chain"), 10),
        ]

        self.add_one_iteration_result()
        self.add_one_iteration_result()
        result = LLMEvaluator(MockLLM.from_multi_line_response(responses)).execute(self.context, Budget(10))
        self.assertEqual(self.to_tuple_message_score(expected), self.to_tuple_message_score(result))
