# ------------------ compatibility aliases for legacy agent demos ------------------
# Older agent demos expect wrapper classes named SearchEmails, ReadEmail, AnswerQuestion, Terminate.
# Provide aliases to the new tool classes to maintain backward compatibility.
SearchEmails = SearchEmailsTool  # type: ignore
ReadEmail = ReadEmailTool        # type: ignore
AnswerQuestion = AnswerQuestionTool  # type: ignore
Terminate = TerminateTool        # type: ignore 

    async def _obs(self, priv: Dict[str, Any], pub: Dict[str, Any]):
        if self.custom_obs:
            return await self.custom_obs.get_observation(pub, priv)
        return {**pub, **priv}


# ------------------ compatibility aliases for legacy agent demos ------------------
# Older agent demos expect wrapper classes named SearchEmails, ReadEmail, AnswerQuestion, Terminate.
# Provide aliases to the new tool classes to maintain backward compatibility.
SearchEmails = SearchEmailsTool  # type: ignore
ReadEmail = ReadEmailTool        # type: ignore
AnswerQuestion = AnswerQuestionTool  # type: ignore
Terminate = TerminateTool        # type: ignore 