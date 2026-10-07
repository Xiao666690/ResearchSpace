"""Conservative extraction of exact, source-located paper claims."""

import json
import re

from pydantic import BaseModel

from core.skills.base import BaseSkill, SkillResult


class GraphClaimInput(BaseModel):
    context: str


class GraphClaimExtractSkill(BaseSkill):
    name = 'graph_claim_extract'
    description = 'Extract exact claims with chunk IDs from indexed paper text'
    input_model = GraphClaimInput

    async def execute(self, data: GraphClaimInput, ctx: dict) -> SkillResult:
        llm = ctx.get('llm')
        if llm is None:
            return SkillResult(ok=False, error_code='NO_LLM', error_message='模型未就绪')
        prompt = ('从以下论文片段提取最多 5 条明确的研究结论或主张。只复制原文中的完整短句，'
                  '每条必须使用所属片段的 chunk_id。严格输出 JSON：'
                  '{"claims":[{"quote":"原文短句","chunk_id":"片段ID"}]}。\n' + data.context)
        response = llm.invoke(prompt)
        text = response.content if hasattr(response, 'content') else str(response)
        try:
            parsed = json.loads(re.sub(r'^\s*```(?:json)?\s*|\s*```\s*$', '', text.strip(), flags=re.I))
            if not isinstance(parsed.get('claims'), list):
                raise ValueError('claims is not a list')
            return SkillResult(ok=True, output={'claims': parsed['claims'][:5]})
        except (ValueError, TypeError, AttributeError):
            return SkillResult(ok=False, error_code='PARSE_ERROR', error_message='主张抽取结果无效')
