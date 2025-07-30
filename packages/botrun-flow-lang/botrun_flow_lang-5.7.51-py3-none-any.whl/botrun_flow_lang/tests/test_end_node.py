import unittest
import asyncio
from botrun_flow_lang.models.nodes.base_node import NodeType
from botrun_flow_lang.models.nodes.end_node import EndNode, EndNodeData
from botrun_flow_lang.models.nodes.event import NodeRunCompletedEvent
import uuid

from botrun_flow_lang.models.variable import InputVariable


class TestEndNode(unittest.TestCase):
    def test_end_node_data_creation(self):
        end_node = EndNodeData(title="Test End")

        self.assertEqual(end_node.type, NodeType.END)
        self.assertEqual(end_node.title, "Test End")

        # Test that id is a string and can be parsed as a valid UUID
        self.assertIsInstance(end_node.id, str)
        self.assertTrue(uuid.UUID(end_node.id, version=4))

    async def async_test_end_node_run(self):
        end_node = EndNode(
            data=EndNodeData(
                title="Test End",
                input_variables=[
                    InputVariable(node_id="idLLMNodeData", variable_name="llm_output")
                ],
            )
        )
        variable_pool = {"idLLMNodeData": {"llm_output": "Test output"}}

        async for event in end_node.run(variable_pool):
            self.assertIsInstance(event, NodeRunCompletedEvent)
            self.assertEqual(event.outputs, {"final_output": "Test output"})

    def test_end_node_run(self):
        asyncio.run(self.async_test_end_node_run())


if __name__ == "__main__":
    unittest.main()
