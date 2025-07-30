from typing import List

from .lib import Base


class Polls(Base):
    def create(
            self,
            answers: List[str],
            question: str,
            room_id: str,
            multiple_choice: bool = False,
            public_voters: bool = True,
    ):
        return self._make_request('polls.create', payload={
            'answers': answers,
            'question': question,
            'roomId': room_id,
            'multipleChoice': multiple_choice,
            'publicVoters': public_voters,
        })

    def vote(self, msg_id: str, options: List[str]):
        return self._make_request('polls.vote', payload={
            'msgId': msg_id,
            'options': options,
        })

    def get_results(self, msg_id: str):
        return self._make_request(
            'polls.results', params={'msgId': msg_id}, method='get',
        )

    def get_votes(self, msg_id: str):
        return self._make_request(
            'polls.votes', params={'msgId': msg_id}, method='get',
        )

    def retract(self, msg_id: str):
        return self._make_request(
            'polls.retractVote',
            payload={'msgId': msg_id},
        )
