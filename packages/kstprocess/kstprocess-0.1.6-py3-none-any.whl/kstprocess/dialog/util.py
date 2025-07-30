from typing import Optional, List
import time
import re
import json
from typing import Optional, List
import falcon
import setproctitle
import os
from openai import OpenAI
import configparser
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation import GenerationConfig
import torch
from loguru import logger
from transformers import AutoTokenizer
from typing import Optional, List, Dict
from datetime import datetime
import json
import re
from vllm import LLM, SamplingParams
from ltp import StnSplit
from kstprocess.dialog.postprocess import ActionProcessor, SentPostProcess
from kstprocess.dialog.prompt_rule_module import PromptRuleService
from abc import ABC, abstractmethod



class QwenBatchInference(object):
    """
        动态 p值。
        支持 transformers, vllm, openai 形式启动。
    """
    def __init__(self, llm_config) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(
            llm_config["tokenizer_path"],
            padding_side='left',
        )
        self.llm_config = llm_config
        self.deployment_type = llm_config["deployment_type"]
        # 加载分句模型
        self.sentence_split_model = StnSplit()
        self.max_tokens = self.llm_config["max_tokens"]
        #### transformers 启动  ####
        if self.deployment_type in ["transformers"]:
            self.model = AutoModelForCausalLM.from_pretrained(
                            llm_config["model_path"],
                            pad_token_id=self.tokenizer.pad_token_id,
                            torch_dtype=torch.bfloat16,)
            self.max_length =  llm_config["max_length"]
            self.model.generation_config = GenerationConfig.from_pretrained(self.llm_config["model_path"],
                                                                            pad_token_id=self.tokenizer.pad_token_id,
                                                                            do_sample=self.llm_config["do_sample"],
                                                                            top_p=float(self.llm_config["top_p"]),
                                                                            repetition_penalty=float(self.llm_config["repetition_penalty"]),
                                                                            temperature=float(self.llm_config["temperature"]),
                                                                            )
            self.model.cuda().eval()
        elif self.deployment_type in ["vllm", "Vllm"]:
            self.model = LLM(model=self.llm_config["model_path"],
                             max_model_len=self.max_length,
                             enforce_eager=True,
                             trust_remote_code=True,
                             enable_prefix_caching=True,
                             dtype="auto")
            self.sampling_params = SamplingParams(top_p=float(self.llm_config["top_p"]),
                                                  temperature=float(self.llm_config["temperature"]),
                                                  repetition_penalty=float(self.llm_config["repetition_penalty"]),
                                                  max_tokens=self.max_tokens)
        elif self.deployment_type in ["openAI_server"]:
            self.base_url =  llm_config["base_url"] 
            self.local_vllm_client = OpenAI(api_key = "zj",
                base_url=self.base_url)
        
        #### 加载后处理模块 ####
        self.sent_post_process_cursor = SentPostProcess()
        self.actionProcess = ActionProcessor()

    def generate_text_list(self, generate_mode: Optional[str], 
                                 qwen_format_history:Optional[List],
                                 text_list: Optional[List]):
        """
            qwen_format_history, text_list 都是 拼接之后的结果
        """
        if generate_mode == "warm_up":
            self.model.generation_config.temperature = 1.1
            self.model.generation_config.top=  1
            logger.info(f"AI warm_up: temperature({self.model.generation_config.temperature}) top({self.model.generation_config.top})")
        else:
            self.model.generation_config.temperature =float(self.llm_config["temperature"])
            self.model.generation_config.top =  float(self.llm_config["top_p"])
            logger.info(f"AI chat: temperature({self.model.generation_config.temperature}) top({self.model.generation_config.top})")

        if self.deployment_type in ["transformers"]:
            batch_input_ids = self.tokenizer.batch_encode_plus(text_list, truncation=True,padding=True, return_tensors='pt').input_ids.cuda()
            generated_ids = self.model.generate(
            batch_input_ids,
            eos_token_id = 151645,     
            max_new_tokens=self.max_tokens,
            )     
            generated_text_list = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)

        elif self.deployment_type in ["vllm", "VLLM", "vLLM"]:
            outputs = self.model.generate(text_list, self.sampling_params, use_tqdm=False)
            for output in outputs:
                generated_text = output.outputs[0].text
                generated_text_list.append(generated_text)

        elif self.deployment_type in ["openAI_server"]:
            response = self.local_vllm_client.chat.completions.create(
                model="paediastrics_server",  
                messages=qwen_format_history,
                top_p=self.model.generation_config.top,
                max_tokens=self.max_tokens,
                temperature=self.model.generation_config.temperature,
            )
            for choice in response.choices:
                content = choice.message.content
                generated_text_list.append(content)


        if self.deployment_type not in ["openAI_server", "vllm", "VLLM", "vLLM"]:
            end_list = []
            for _, res in enumerate(generated_text_list):
                sent = res.split("assistant")[-1]
                end_list.append(sent)
        else:
            end_list = generated_text_list
        return generated_text



class MedicalAdvertisingChatBotGenerator(ABC):
    def __init__(self, domain, source) -> None:
        self.config = configparser.ConfigParser()
        self.config.read('./config/sever.ini')
        setproctitle.setproctitle(self.config["generate_config"]["setproctitle"])
        os.environ["CUDA_VISIBLE_DEVICES"]=self.config["generate_config"]["devices"]
        logger.info("model already")
        self.prompt_rule_service = PromptRuleService(self.config["other"]["simModelPath"], 
                                                     float(self.config["other"]["simModelThreshold"]))
        self.generate_model = QwenBatchInference(self.config["generate_config"])
        self.domain = domain
        self.source = source

    def __add_user_utterance_to_history(self, history:Optional[List], query:Optional[str])->Optional[List]:
        new_history = history.copy()
        new_history.append( 
                {
                    "msgId": "",
                    "role": "CLIENT",
                    'subType': 'INPUT_VISITOR',
                    "sentence": query
                }
                )
        return new_history
    
    ### 计算中控对话的轮次 ###
    def __count_dialogure_round(self, dialog_record:Optional[List]):
        r0 = [record["role"].lower() for record in dialog_record]
        r0t = "".join(r0)
        r0t = r0t.replace("client","C")
        r0t = re.findall("C{1,}", r0t)
        self.server_round = len(r0t)


    def add_prompt_to_history_and_convert_history_format_to_qwen(self, prompt:Optional[str], history:Optional[List[Dict]]):
        if len(prompt) > 0:
            format_history = [{"role": "system", "content": prompt}]
        else:
            format_history = []
        i = 0
        while i < len(history):
            cur_query = ""
            # "ROBOT_GUIDE"  引导语  "ROBOT_GREETING" 问候语
            while (i<len(history)) and "subType" in history[i].keys() and history[i]["subType"] in ["kw", "skw", "ROBOT_GREETING"]:
                i += 1
            while (i< len(history) and history[i]["role"] == "CLIENT" ):
                cur_query += history[i]["sentence"] + "<sep>"
                i += 1
            if len(cur_query) > 0:
                cur_query = re.sub("^<sep>", "", cur_query)
                cur_query = re.sub("<sep>$", "", cur_query)
                format_history.append({"role":"user", "content": "访客问题:"+cur_query.rstrip("<sep>")})
            cur_response = ""
            while i< len(history) and history[i]["role"] == "SERVER":
                cur_response += history[i]["sentence"] + "<sep>"
                i += 1
            if len(cur_response) > 0:
                cur_response = re.sub("^<sep>", "", cur_response)
                cur_response = re.sub("<sep>$", "", cur_response)
                format_history.append({"role":"assistant", "content":cur_response.rstrip("<sep>")}) 
        logger.info(f'current prompt length:{sum([len(item["content"]) for item in format_history])}')
        return format_history


    def pipeline_for_AI_warmupWord(self):
        self.keyword = self.input_params.get("keyword")
        user_utterance = self.input_params.get("utterance", str)
        dialogRecord = self.input_params.get("dialogRecord", [])
        limit =  self.input_params.get("limit", 5)
        prompt_info = self.input_params.get("promptInfo", {'prompt_mapping': [], 'prompt_acp': [], 'prompt_artificial': []})
        dialogRecord = self.__add_user_utterance_to_history(dialogRecord, 
                                                            user_utterance)
        self.__count_dialogure_round(dialogRecord)

        logger.info("=========="*8)
        logger.info("=====AI_warmupWord====="*4)
        logger.info("session_id:"+str(self.session_id))
        logger.info("server_round:"+str(self.server_round))
        
        format_dialog_record = []
        for line in dialogRecord:
            format_dialog_record.append(line["role"]+":"+line["sentence"])
        format_dialog_record = "\n".join(format_dialog_record)

        basic_action_label_list = [[ac] for ac in prompt_info["prompt_artificial"]]
        logger.info("use_action:"+str(basic_action_label_list))
        generate_start_time = time.time()
        template_qa = None
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.guide_text = ""
        self.guide_text += "<sep>".join(
            line["sentence"] for line in dialogRecord 
            if "subType" in line.keys() 
            and line["role"] == "SERVER" 
            and line["subType"] == "ROBOT_GUIDE"
        )
        
        prefix_prompt = f"你是[{self.domain}][{self.source}]，你的核心目标：是获取访客的联系方式。当前时间：{current_time} \n搜索词:{self.keyword}\n引导语:{self.guide_text}"
        qwen_format_history = self.add_prompt_to_history_and_convert_history_format_to_qwen(prefix_prompt, dialogRecord)
        generate_mode = "warm_up"
        response = self.generate_model.batch_inference( qwen_format_history=qwen_format_history,
                                                        template_qa=template_qa,
                                                        generate_mode=generate_mode,
                                                        server_round=self.server_round, 
                                                        action_label_list=basic_action_label_list, 
                                                        limit=limit)
        generate_end_time = time.time()
        du_response = self.prompt_rule_service.self_deduplicate(response)
        logger.info(f"执行暖场语去重:{len(response)}->{len(du_response)}")
        for i, _ in enumerate(du_response):
            logger.info(f"去重后暖场语:{du_response[i]}")

        logger.info(f"cost time: {round(generate_end_time-generate_start_time, 2)}s")
        logger.info("##"*50)
        logger.info("=========="*4)
        logger.info("=========="*4)
        logger.info("")
        return du_response
    
    @abstractmethod
    def pipeline_for_AI_chat():
        pass

    def on_post(self, requests_data, response_data):
        ### 接受参数 ###
        input_params = json.load(requests_data.bounded_stream)
        self.input_params = input_params
        self.session_id = input_params.get("dialogId")
        self.task_type = input_params.get("task_type")
        if self.task_type in ["dialog", "smartScript"]:
            response, basic_action_label_list = self.pipeline_for_AI_chat()
        elif self.task_type in ["warmup"]:
            response = self.pipeline_for_AI_warmupWord()
            prompt_info = self.input_params.get("promptInfo", {'prompt_mapping': [], 'prompt_acp': [], 'prompt_artificial': []})
            basic_action_label_list = prompt_info["prompt_artificial"]
        else:
            raise NotImplementedError(f"not support this task_type: {self.task_type}")


        result = {
            "code": 200,
            "session_id": self.session_id,
            "data": response,
            "action": basic_action_label_list,
            "version": self.config["generate_config"]["version"], 
        }

        response_data.text = json.dumps(result)
        response_data.status = falcon.HTTP_200