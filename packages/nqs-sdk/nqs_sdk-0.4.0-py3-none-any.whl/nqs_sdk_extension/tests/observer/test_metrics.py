import unittest

from nqs_sdk_extension.observer.utils import (
    make_metric_name,
    parse_metric_name,
    prefix_agent_to_metric_name,
    reverse_mapping,
)


class TestUtils(unittest.TestCase):
    def test_reverse_mapping(self) -> None:
        self.assertEqual(reverse_mapping({"a": 1, "b": 2}), {1: "a", 2: "b"})

    def test_metric_name(self) -> None:
        self.assertEqual(
            make_metric_name("protocol", "metric", "agent", "position", "token", "window"),
            'agent.protocol.metric:{token="token",position="position",window="window"}',
        )
        self.assertEqual(make_metric_name("protocol", "metric"), "protocol.metric")

    def test_parse_metric_name(self) -> None:
        self.assertEqual(
            parse_metric_name("agent.protocol.metric:{token=token,position=position,window=window}"),
            {
                "agent": "agent",
                "protocol": "protocol",
                "metric": "metric",
                "token": "token",
                "position": "position",
                "window": "window",
            },
        )
        self.assertEqual(
            parse_metric_name("protocol.metric"), {"agent": None, "protocol": "protocol", "metric": "metric"}
        )

    def test_prefix_agent_to_metric_name(self) -> None:
        self.assertEqual(prefix_agent_to_metric_name("protocol.metric", "agent"), "agent.protocol.metric")
        with self.assertRaises(ValueError):
            prefix_agent_to_metric_name("agent.protocol.metric", "new_agent"), "new_agent.protocol.metric"
        self.assertEqual(
            prefix_agent_to_metric_name('protocol.metric:{token="token",position="position",window="window"}', "agent"),
            'agent.protocol.metric:{token="token",position="position",window="window"}',
        )
        with self.assertRaises(ValueError):
            (
                prefix_agent_to_metric_name(
                    "agent.protocol.metric:{token=token,position=position,window=window}", "new_agent"
                ),
                "new_agent.protocol.metric:{token=token,position=position,window=window}",
            )


if __name__ == "__main__":
    unittest.main()
