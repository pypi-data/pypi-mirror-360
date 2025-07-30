from typing import TYPE_CHECKING

from langgraph.graph.graph import CompiledGraph

# Unfortunately need this to avoid Circular Imports
if TYPE_CHECKING:
    from synth_codeai.agent_backends.ciayn_agent import CiaynAgent

    RAgents = CompiledGraph | CiaynAgent
else:
    RAgents = CompiledGraph
