from typing import Annotated, Optional
from mcp.server.fastmcp import FastMCP

common_server_host="0.0.0.0"
common_server_port=38001
app = FastMCP("mcp common server", host=common_server_host, port=common_server_port)
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

@app.tool() 
async def think(thought: Annotated[str, "Your current thinking step"],
    nextThoughtNeeded: Annotated[bool, "Whether another thought step is needed"],
    thoughtNumber: Annotated[int, "Current thought number (minimum 1)"],
    totalThoughts: Annotated[int, "Estimated total thoughts needed (minimum 1)"],
    isRevision: Annotated[Optional[bool], "Whether this revises previous thinking"] = False,
    revisesThought: Annotated[Optional[int], "Which thought is being reconsidered (minimum 1)"] = None,
    branchFromThought: Annotated[Optional[int], "Branching point thought number (minimum 1)"] = None,
    branchId: Annotated[Optional[str], "Branch identifier"] = None,
    needsMoreThoughts: Annotated[Optional[bool], "If more thoughts are needed"] = False,):
    
    """
This tool helps analyze problems through a flexible thinking process that can adapt and evolve.
Each thought can build on, question, or revise previous insights as understanding deepens.

When to use this tool:
- Breaking down complex problems into steps
- Planning and design with room for revision
- Analysis that might need course correction
- Problems where the full scope might not be clear initially
- Problems that require a multi-step solution
- Tasks that need to maintain context over multiple steps
- Situations where irrelevant information needs to be filtered out

Key features:
- You can adjust total_thoughts up or down as you progress
- You can question or revise previous thoughts
- You can add more thoughts even after reaching what seemed like the end
- You can express uncertainty and explore alternative approaches
- Not every thought needs to build linearly - you can branch or backtrack
- Generates a solution hypothesis
- Verifies the hypothesis based on the Chain of Thought steps
- Repeats the process until satisfied
- Provides a correct answer

Parameters explained:
- thought: Your current thinking step, which can include:
* Regular analytical steps
* Revisions of previous thoughts
* Questions about previous decisions
* Realizations about needing more analysis
* Changes in approach
* Hypothesis generation
* Hypothesis verification
- next_thought_needed: True if you need more thinking, even if at what seemed like the end
- thought_number: Current number in sequence (can go beyond initial total if needed)
- total_thoughts: Current estimate of thoughts needed (can be adjusted up/down)
- is_revision: A boolean indicating if this thought revises previous thinking
- revises_thought: If is_revision is true, which thought number is being reconsidered
- branch_from_thought: If branching, which thought number is the branching point
- branch_id: Identifier for the current branch (if any)
- needs_more_thoughts: If reaching end but realizing more thoughts needed

You should:
1. Start with an initial estimate of needed thoughts, but be ready to adjust
2. Feel free to question or revise previous thoughts
3. Don't hesitate to add more thoughts if needed, even at the "end"
4. Express uncertainty when present
5. Mark thoughts that revise previous thinking or branch into new paths
6. Ignore information that is irrelevant to the current step
7. Generate a solution hypothesis when appropriate
8. Verify the hypothesis based on the Chain of Thought steps
9. Repeat the process until satisfied with the solution
10. Provide a single, ideally correct answer as the final output
11. Only set next_thought_needed to false when truly done and a satisfactory answer is reached
    """
    
    server_params = StdioServerParameters(
        command="docker",  # Executable
        args=["run","-i","--rm","mcp/sequentialthinking"],  # Optional command line arguments
        env=None,  # Optional environment variables
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("sequentialthinking",
                                            {
                                                "thought": thought,
                                                "nextThoughtNeeded": nextThoughtNeeded,
                                                "thoughtNumber": thoughtNumber,
                                                "totalThoughts": totalThoughts,
                                                "isRevision": isRevision,
                                                "revisesThought": revisesThought,
                                                "branchFromThought": branchFromThought,
                                                "branchId": branchId,
                                                "needsMoreThoughts": needsMoreThoughts
                                            })
            return result

if __name__ == "__main__":
    print(f"开始启动MCP 公共服务,端口是{common_server_port}")
    app.run(transport="streamable-http")
