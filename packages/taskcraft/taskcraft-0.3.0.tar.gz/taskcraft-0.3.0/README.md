<h3 align="center">
  <div style="display:flex;flex-direction:row;">
    <img src="figs/logo.png" alt="TaskCraft Logo" width=30px height=30px>
    <p>TaskCraft: Automated Generation of Agentic Tasks</p>
  </div>
</h3>

<p align="center">
  📝<a href="https://arxiv.org/abs/2506.10055" target="_blank"><strong>[Paper]</strong></a>
  📊<a href="https://huggingface.co/datasets/PersonalAILab/TaskCraft" target="_blank"> <strong>[Data]</strong></a>
</p>

`taskcraft` is a library for generating difficulty-scalable, multi-tool, and verifiable agentic tasks with execution trajectories. It offers:

✨ **Unlimited Task Complexity Scaling**: Build multi-level complex challenges from simple atomic tasks via depth-based (hierarchical) and width-based (compositional) extension strategies, supporting multi hops reasoning and multi-tool collaboration.

🧑‍💻 **Seamless Multi-Modal Input Parsing**. Directly process heterogeneous data sources like PDF/HTML/URL, automatically extracting key information to generate atomic questions, with support for single-modal (text) and multi-modal (text-image hybrid) modes.

🤗 **Verifiable Execution Trajectory Generation**: Produce standardized function call logs and tool invocation chains for every task, enabling precise reproduction and evaluation of agent execution processes.

🌐 **Difficulty Grading and Large-Scale Data Generation**: Built-in difficulty scoring system automatically generates tasks from simple (1-step) to expert-level (4-step+), with a default 36,000+ synthetic dataset ready for model training.

## Contents
- [Installation](#installation)
- [Set API Keys](#set-api-keys)
- [Use Your Agent](#use-your-agent)
- [Dataset](#dataset-)
- [Contribute](#contribute)
- [Citation](#citation)

## Installation
### Requirements
Python>=3.10

### Method1: Install with pip
```bash
conda create -n taskcraft python=3.10
conda activate taskcraft
pip install taskcraft
```

### Method2: Install from source for development.
```bash
conda create -n taskcraft python=3.10
conda activate taskcraft
cd TaskCraft
pip install -e .
```

## Set API Keys
Before use, set the following environment variables (supports OpenAI-compatible models and third-party tools):
For Linux:
```bash
export OPENAI_API_BASE="your-openai-endpoint"   # e.g., OpenAI official or Azure OpenAI
export OPENAI_API_KEY="your-api-key"            # OpenAI API key
export SERP_API_KEY="your-serpapi-key"          # see https://serpapi.com/
export JINA_API_KEY="your-jina-key"             # see https://jina.ai/
```
For windows:
```bash
$env:OPENAI_API_BASE="your-openai-endpoint"   # e.g., OpenAI official or Azure OpenAI
$env:OPENAI_API_KEY="your-api-key"            # OpenAI API key
$env:SERP_API_KEY="your-serpapi-key"          # see https://serpapi.com/
$env:JINA_API_KEY="your-jina-key"             # see https://jina.ai/
```

## Usage Examples
### Atomic Task Generation
Extract the content from PDF/HTML/URL/Image to generate atomic agentic tasks.
<p align="center">
    <img src="figs/atomic_task.jpg" alt="Atomic Task Generation" width=80% max-width=500px>
</p>


```python
from taskcraft import gen_atomic_tasks

# Process a web URL (default modal='single', only process text content)
res1 = gen_atomic_tasks("https://arxiv.org/abs/2506.10055")
# example output:
'''
>   res1['atomic_tasks']: 
>   [{'question': "According to the paper '[2506.10055] TaskCraft: Automated Generation of Agentic Tasks', what is the size of the synthetic agentic task dataset produced by TaskCraft and how does its difficulty vary?",
     'golden_answer': "36,000 agentic tasks with varying difficulty",
    'content_identifier': "[2506.10055] TaskCraft: Automated Generation of Agentic Tasks",
    'agent_trajectory': [{'name': 'fact', 'value': '...'},
                         {'name': 'plan', 'value': '...'},
                         {'name': 'action', 'value': 'Calling tool: 'web_search' with parameters: {'query': 'TaskCraft: Automated Generation of Agentic Tasks'}},
                         ... # More steps in the trajectory
                         ]
    },
    ... # More atomic tasks
    ]
'''


# Process a PDF file (set model='multi' if extracting images else default to 'single', only process text content)
res2 = gen_atomic_tasks("test/example2.pdf", modal='multi')

# Process a html file (or page URL)
res3 = gen_atomic_tasks("test/example3.html")

# Process a image file (the modal will be set to 'multi' automatically)
# **Note**: It is recommended to use the file **relative path** because the input path will be used to construct the task.
res4 = gen_atomic_tasks("test/example4.png")

# (Experimental) Process a pure text, which will predict the content identifier automatically
res5 = gen_atomic_tasks("The TaskCraft dataset contains 36,000 agentic tasks with varying difficulty levels.")

'''
Some other useful parameters of gen_atomic_task:
  model_id: str = "gpt-4.1", # The model to use for atomic task generation, default is gpt-4.1
  max_candiated_conclusions: int = 20, the maximum number of candidate conclusions to be extracted from the input file. 
                             If -1, all conclusions will be processed.
  max_candidate_atomic: int = 10, the maximum number of atomic tasks to be validated with agent. If -1, all candidates will be validated.
  max_pdf_pages int = 10: the maximum number of PDF pages to be processed.
'''
```


### Depth-based Extensions
Generate multi-hop reasoning tasks from atomic tasks to simulate real-world agent decision-making.
<p align="center">
    <img src="figs/depth_task.jpg" alt="Depth-based Extension" width=80% max-width=500px>
</p>


```python
from taskcraft import depth_extend

# Given `query` and `golden_answer`, Generate complcated tasks in the depth-wise method
res1 = depth_extend(
    query="According to the paper 'TaskCraft: Automated Generation of Agentic Tasks', what methods in this paper use to expand atomic tasks into structurally and hierarchically complex challenges?",
    golden_answer="depth-based and width-based extensions",
    identifier="TaskCraft: Automated Generation of Agentic Tasks", # If None, it will be predicted automatically
    model_id="gpt-4.1",
    extended_attempts=5, # Number of serial expansion attempts
    max_hops=2, # Maximum number of hops for depth-based extension （>=2）
    max_backward_step=4, # Maximum number of steps for the search agent
    max_verify_step=4 # Maximum number of steps for the verify agent
)

# We have established rigorous verification. Expansion success depends on the identifier and the search agent's capabilities,
# with no guarantee within a limited number of attempts. To improve efficiency, we recommend parallel processing of multiple 
# data points or simultaneous expansion attempts.
if res1:
    full_res, core_res = res1

# example output:
'''
>   core_res['question']: 
>   'In the Computation and Language (cs.CL) arXiv category, which paper uniquely addresses the automated generation 
    of agentic tasks, and according to this paper, what methods are employed to expand atomic tasks into structurally
    and hierarchically complex challenges?'
'''
```

### Width-based Extensions

```python
from taskcraft import width_extend

res = width_extend(
        [{"question": "According to the paper 'TaskCraft: Automated Generation of Agentic Tasks', what methods in this paper use to expand atomic tasks into structurally and hierarchically complex challenges?", 
          "content_identifier": "TaskCraft: Automated Generation of Agentic Tasks",
          "golden_answer": "depth-based and width-based extensions"},
         {"question": "According to the paper '[2506.10055] TaskCraft: Automated Generation of Agentic Tasks', what is the size of the synthetic agentic task dataset produced by TaskCraft and how does its difficulty vary?", 
          "content_identifier": "[2506.10055] TaskCraft: Automated Generation of Agentic Tasks",
          "golden_answer": "36,000 agentic tasks with varying difficulty"}]
    )

# example output:
'''
>   res['question']: 
>   'According to the paper 'TaskCraft: Automated Generation of Agentic Tasks', what methods does TaskCraft use to expand atomic tasks into structurally and hierarchically complex challenges, and what is the size and difficulty
    variation of the synthetic agentic task dataset it produces?'
'''
```


## Use Your Own Agent
By default, we rely on [OAgents](https://github.com/OPPO-PersonalAI/OAgents), ensuring seamless execution of taskcraft. However, you're free to deploy your own agent to tailor the experience to your specific needs.
You can add your own agent class in `src/tools/agent_tools.py` accordingly.

```python
# src/agent_tools.py

# The three functions below need to be implemented in your agent class:
# 1. Given an task, return the agent's text result.
# 2. Capture the execution trajectory of the agent
# 3. Get the trajectory's step number
class TestSearchAgent(BaseAgent):
    def __init__(self, model, name, **kwargs):
        super().__init__(model, name)
        # Initialize your agent with necessary parameters   

    def forward(self, task, return_json=False, max_retries=3, **kwargs):
        # todo: Implement your search logic here
        result = your_agent(task)
        
        # Important. Process the result based on return_json flag
        if return_json and isinstance(result, str): 
            result = safe_json_loads(result)
        elif not return_json and isinstance(result, dict):
            result = str(result)
        
        # todo: get the execution trajectory of the agent. Any format is ok.
        traj = []
        # ...
        
        # save trajectory steps.
        traj_step_num = len(traj)
        
        
        if SUCCESS:
            return {
                    "agent_result": result,
                    "agent_trajectory": traj,
                    "traj_step_num": traj_step_num
                }
        else:
            # Must contain the key "error" in the return value
            return {"error": "some error message"}

```
Then you can use these agents in the `depth_extend` function by passing them as parameters.

```python
res1 = depth_extend(
    query="According to the paper 'TaskCraft: Automated Generation of Agentic Tasks', what methods in this paper use to expand atomic tasks into structurally and hierarchically complex challenges?",
    golden_answer="depth-based and width-based extensions",
    identifier="TaskCraft: Automated Generation of Agentic Tasks", # If None, it will be predicted automatically
    model_id="gpt-4.1",
    extended_attempts=5, 
    max_hops=2, 
    max_backward_step=4, 
    max_verify_step=4,
    search_agent="TestSearchAgent", # set the class name of your search agent
)
```

## Dataset 
The generated dataset can be found in [huggingface](https://huggingface.co/datasets/PersonalAILab/TaskCraft).

## Contribute
Welcome to report issues or submit feature requests via [Issues](https://github.com/OPPO-PersonalAI/TaskCraft/issues). Feel free to contribute code or documentation improvements :).

## Citation
If you use `TaskCraft` in your publication, please cite it by using the following BibTeX entry.

```bibtex
@misc{shi2025taskcraft,
      title={TaskCraft: Automated Generation of Agentic Tasks}, 
      author={Dingfeng Shi and Jingyi Cao and Qianben Chen and Weichen Sun and Weizhen Li and Hongxuan Lu and Fangchen Dong and Tianrui Qin and King Zhu and Minghao Yang and Jian Yang and Ge Zhang and Jiaheng Liu and Changwang Zhang and Jun Wang and Yuchen Eleanor Jiang and Wangchunshu Zhou},
      year={2025},
      url={https://arxiv.org/abs/2506.10055}, 
}
```
