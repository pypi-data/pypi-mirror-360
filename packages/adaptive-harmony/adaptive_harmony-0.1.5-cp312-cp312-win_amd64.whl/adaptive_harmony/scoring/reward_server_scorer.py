from adaptive_harmony.scoring.base_scorer import Scorer, ScoreWithMetadata
from adaptive_harmony.core.reward_client.client import RewardClient, Turn, Request
from adaptive_harmony import StringThread


class RewardServerScorer(Scorer):

    def __init__(self, reward_server_ip: str):
        super().__init__()
        self.reward_client = RewardClient(reward_server_ip)

    async def setup(self):
        await self.reward_client.setup()

    async def score(self, string_thread: StringThread) -> ScoreWithMetadata:
        response = await self.reward_client.score(
            Request(
                turns=[Turn(content=turn.content, role=turn.role) for turn in string_thread.turns()],
                metadata=string_thread.metadata,
            )
        )
        return ScoreWithMetadata(score=response.reward)
