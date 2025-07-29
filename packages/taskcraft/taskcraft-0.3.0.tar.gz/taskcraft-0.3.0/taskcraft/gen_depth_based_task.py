# -*- coding: utf-8 -*-
# @Project      : taskcraft
# @File         : gen_depth_based_task.py
# @Author       : Dingfeng Shi <shidingfeng@outlook.com>, Jingyi Cao <224040283@link.cuhk.edu.cn>, Qianben Chen <chenqianben@oppo.com>
# @LastUpdated  : 2025/6/11
# @LICENSE      : Apache License 2.0
import types
from typing import Optional, List

from .agent_tools import *
from .oagents import OpenAIServerModel
from .utils import CUSTOM_ROLE_CONVERSIONS, run_llm_prompt, load_yaml, check_envs

# load prompt templates
verify_prompt_yaml_path = Path(__file__).parent / "prompts/verify_prompts.yaml"
verify_prompt_template = load_yaml(verify_prompt_yaml_path)
depth_prompt_yaml_path = Path(__file__).parent / "prompts/depth_prompts.yaml"
depth_prompt_templates = load_yaml(depth_prompt_yaml_path)
general_prompt_yaml_path = Path(__file__).parent / "prompts/general_prompts.yaml"
general_prompt_templates = load_yaml(general_prompt_yaml_path)


class DepthExtend:
    def __init__(self, model, search_agent='SearchAgent', verify_agent='VerifyAgent'):
        self.model = model
        self.search_agent = search_agent
        self.verify_agent = verify_agent
        if self.search_agent in globals():
            self.search_agent = globals()[self.search_agent]
        else:
            raise ImportError(f"The agent: {self.search_agent} not found, please check the import path.")

        if self.verify_agent in globals():
            self.verify_agent = globals()[self.verify_agent]
        else:
            raise ImportError(f"The agent: {self.verify_agent} not found, please check the import path.")

        self.prompt_templates = {
            "augmented_question": depth_prompt_templates['augmented_question_prompt'],
            "backward_task_prompt": depth_prompt_templates['backward_task_prompt'],
            "generate_query_prompt": depth_prompt_templates['generate_query_prompt'],
            "is_superset_valid": depth_prompt_templates['is_superset_valid'],
        }

    # element --> search(element) --> superset --> id --> Query
    def backward(self, element, max_step=10, max_retries=3, **kwargs):
        backward_agent = self.search_agent(self.model, 'backward_agent', max_step=max_step, **kwargs)

        # 1. Generate relation and superset
        backward_question = self.prompt_templates['backward_task_prompt'].format(element=element)
        backward_result = backward_agent(backward_question, return_json=True,
                                         max_retries=max_retries)  # agent_result, agent_trajectory
        if isinstance(backward_result, dict) and "error" in backward_result:
            return backward_result
        backward_result = backward_result["agent_result"]  # identifier, relation

        # 2. Check if superset is valid
        developer_prompt = self.prompt_templates['is_superset_valid']
        prompt = f'''
                Given superset: {backward_result['identifier']}\n
                Given relationship: {backward_result['relation']}\n
                Given subset: {element}\n
                '''
        query_check = run_llm_prompt(self.model, prompt, developer_prompt, return_json=True, max_retries=max_retries)
        if "error" in query_check:
            return query_check
        if query_check == "invalid":
            backward_result["error"] = "error superset"
            return backward_result

        # 3. Generate question based on superset and relation
        developer_prompt = self.prompt_templates['generate_query_prompt']
        prompt = f'''
                Certain answer: {element}\n
                Identifier: {backward_result['identifier']}\n
                Relationship: {backward_result['relation']}\n
                '''

        success = False
        for _ in range(3):
            try:
                query = run_llm_prompt(self.model, prompt, developer_prompt, return_json=True,
                                       max_retries=max_retries)  # new_query
                if "error" in query:
                    return query
                query = query['new_query']
                success = True
                break
            except Exception as e:
                logging.warning("[Failed]: Exception occurred while generating query: " + str(e))
                continue

        if success:
            return {
                'query': query, 'element': element,
                'identifier': backward_result['identifier'], 'relation': backward_result['relation'],
            }
        else:
            logging.warning("[Failed]: Fail to generate a new query based on the superset.")
            return None

    # query + golden_answer -> verify_result
    def verify(self, query, golden_answer, max_step=10, max_retries=3, **kwargs):
        verify_agent = self.verify_agent(self.model, "oppo_verify_agent", search_agent=self.search_agent,
                                         max_step=max_step, **kwargs)
        verify_result = verify_agent(query, golden_answer, max_retries=max_retries)
        return verify_result


def process_single_task(args):
    # initialze model
    model = OpenAIServerModel(
        args.model_id,
        custom_role_conversions=CUSTOM_ROLE_CONVERSIONS,
        max_completion_tokens=8192,
        api_key=os.environ.get("OPENAI_API_KEY"),
        api_base=os.environ.get("OPENAI_API_BASE"),
    )
    module = DepthExtend(model, search_agent=args.search_agent, verify_agent=args.verify_agent)

    # check identifier, if it is None, should be initialized
    if args.identifier is None:
        logging.info("Identifier is not provided, generating identifier...")
        developer_prompt = general_prompt_templates["get_identifier_prompt"]
        prompt = f"""Now process this question: {args.query}"""
        identifier_result = run_llm_prompt(model, prompt, developer_prompt=developer_prompt, return_json=True)
        args.identifier = identifier_result["content_identifier"]

    full_results = []
    full_query = args.query
    last_identifier = args.identifier
    full_results.append({
        'initial_query': full_query,
        'initial_answer': args.golden_answer,
        'initial_trajectory': args.trajectory,
        'initial_identifier': last_identifier,
        'valid_hop': 1
    })

    valid_hop = 1
    for hop in range(args.extended_attempts):
        logging.info(f"The {hop + 1} attempt to extend the query")

        # step1 backward
        backward_result = module.backward(last_identifier, max_step=args.max_backward_step)
        if isinstance(backward_result, dict) and "error" in backward_result:
            logging.warning(f"[Failed]: The extended task in the {hop} attempt failed in backward.")
            continue
        now_query = backward_result["query"]
        logging.info(f"The generated intermediate task in the {hop + 1} attempt: {now_query}")

        # step2 check now query result
        logging.info(f"start agentic verify...")
        backward_verify_result = module.verify(now_query, last_identifier, max_step=args.max_verify_step)
        if isinstance(backward_verify_result, dict) and "error" in backward_verify_result:
            logging.warning(f"[Failed]: The intermediate query fail the agentic verification.")
            continue

        # # if agent can not answer correcly, then the agent trajectory is wrong
        if backward_verify_result["agent_score"] <= 0:
            logging.warning(f"[Failed]: The extended task in the {hop} attempt failed because llm can solve it.")
            continue

        # step3 query merge
        success = False
        for _ in range(5):
            try:
                developer_prompt = depth_prompt_templates['merge_query_prompt']
                prompt = f"""
                        Core query: {full_query}
                        Auxiliary query: {now_query}
                        Element to be replaced: {last_identifier} 
                        """.strip()
                new_query = run_llm_prompt(model, prompt, developer_prompt, return_json=True)  # analysis, new_query
                if isinstance(new_query, dict) and "error" in new_query:
                    logging.warning(f"[Failed]: Fail to merge a new query.")
                    continue
                new_query = new_query['new_query']

                # judge new query
                query_compare_prompt = depth_prompt_templates['query_compare_prompt'].format(
                    last_identifier=last_identifier,
                    new_task=new_query,
                    full_query=full_query,
                    golden_answer=args.golden_answer
                )

                query_judge = run_llm_prompt(model, query_compare_prompt, developer_prompt=None,
                                             return_json=True)  # analysis, is_valid
                if isinstance(query_judge, dict) and "error" in query_judge:
                    logging.warning(f"[Failed]: Fail to judge the merged query. The merged query is: {new_query}")
                    continue
                if not query_judge["is_valid"]:
                    logging.warning(
                        f"\n-----------------------------------------\n[Failed]: The merged query expression do not pass semantic analysis. \n[Core query]: {full_query}. \n[Auxiliary query]: {now_query}.\n [Merged query]: {new_query}\n-----------------------------------------\n")
                    continue
                success = True
                break
            except Exception as e:
                logging.warning("[Failed]: Exception occurred while merging query: " + str(e))
                continue

        if not success:
            logging.warning(f"[Failed]: Fail to merge a new query in 5 tries.")
            continue

        valid_hop += 1
        logging.info(f"[Success]: The extended task in the {hop + 1} attempt: {new_query}")

        full_results.append({
            "query": now_query,
            "answer": last_identifier,
            "valid_hop": 1,
            "trajectory": backward_verify_result['agent_trajectory'],
            "agent_score": backward_verify_result["agent_score"],
            "llm_score": backward_verify_result["llm_score"]
        })

        full_results.append({
            "query": new_query,
            "answer": args.golden_answer,
            "valid_hop": valid_hop,
            "trajectory": None,
            "agent_score": None,
            "llm_score": None
        })
        last_identifier = backward_result['identifier']
        full_query = new_query
        if valid_hop >= args.max_hops:
            logging.info(f"Reach the max hops: {args.max_hops}, stop extending.")
            break

    if len(full_results) == 1:
        logging.warning(f"Failed to extend the query in {args.extended_attempts} tries.")
        return None

    # postprocess trajectory
    solve_trajectory = {
        "question": full_results[-1]["query"],
        "golden_answer": full_results[-1]["answer"],
        "trajectory": [],
    }
    solve_trajectory["trajectory"].append({
        "sub_query": full_results[0]["initial_query"],
        "sub_answer": full_results[0]["initial_answer"],
        "sub_trajectory": full_results[0].get("trajectory", None)
        # None if the initial query does not have a trajectory
    })
    for i in range(1, len(full_results), 2):
        item = full_results[i]
        assert item["trajectory"] is not None
        solve_trajectory["trajectory"].append({
            "sub_query": item["query"],
            "sub_answer": item["answer"],
            "sub_trajectory": item["trajectory"]
        })
    solve_trajectory["trajectory"] = solve_trajectory["trajectory"][::-1]
    return full_results, solve_trajectory


def depth_extend(
        query: str,
        golden_answer: str,
        identifier: str = None,
        trajectory: Optional[List] = None,
        model_id: str = "gpt-4.1",
        extended_attempts: int = 4,
        max_hops=2,
        max_backward_step=10,
        max_verify_step=10,
        search_agent='SearchAgent',
        verify_agent='VerifyAgent'
):
    if search_agent == 'SearchAgent':
        check_envs()

    args = types.SimpleNamespace(
        query=query,
        golden_answer=golden_answer,
        identifier=identifier,
        model_id=model_id,
        extended_attempts=extended_attempts,
        max_hops=max_hops,
        max_backward_step=max_backward_step,
        max_verify_step=max_verify_step,
        search_agent=search_agent,
        verify_agent=verify_agent,
        trajectory=trajectory
    )
    ret = process_single_task(args)
    return ret


if __name__ == '__main__':
    res = depth_extend(
        query="According to the paper 'Block Circulant Adapter for Large Language Models', how does the parameter count of BCA method compare to VeRA in fine-tuning large language models?",
        golden_answer="14 times fewer",
        identifier="Block Circulant Adapter for Large Language Models",
        extended_attempts=5,
        max_hops=2,
        max_backward_step=4,
        max_verify_step=8
    )
