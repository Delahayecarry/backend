from autogen_agentchat.agents import AssistantAgent

from dotenv import load_dotenv
import os
from backend.agents.clients.OpenaiForAssistant import OpenaiForAssistant
from math import exp
import py_trees  

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
model = os.getenv("OPENAI_MODEL")

model_client = OpenaiForAssistant(api_key=api_key, base_url=base_url, model=model)


class EmotionalBehaviorAgent(AssistantAgent):
    def __init__(self, name, model_client, **kwargs):
        super().__init__(name, model_client, **kwargs)
        # --- 情绪维度 (PAD) ---
        self.valence = 0.0   # [-1, 1]  负–正
        self.arousal = 0.0   # [ 0, 1]  平静–激动
        self.dominance = 0.0 # [ 0, 1]  被动–掌控
        # --- 行为状态 ---
        self.state = 'idle'
        # 行为树根节点
        self.behavior_root = self._build_behavior_tree()

    # ---------- 情绪模型 ----------
    def update_emotion(self, event: str):
        """事件评价函数，可根据需要加载外部 JSON/DB 配置"""
        delta_map = {
            'task_failed':     (-0.6, 0.7, -0.2),
            'task_completed':  ( 0.8, 0.6,  0.5),
            'conflict':        (-0.8, 0.8,  0.4),
        }
        dv, da, dd = delta_map.get(event, (0.0, 0.0, 0.0))
        self.valence = self._clip(self.valence + dv)
        self.arousal = self._clip(self.arousal + da, low=0.0)
        self.dominance = self._clip(self.dominance + dd, low=0.0)

    def decay_emotion(self, decay_rate: float = 0.05):
        """每 tick 调用，使情绪逐渐回归基线"""
        self.valence   *= exp(-decay_rate)
        self.arousal   *= exp(-decay_rate)
        self.dominance *= exp(-decay_rate)

    @staticmethod
    def _clip(x, low=-1.0, high=1.0):
        return max(low, min(high, x))

    # ---------- 行为模型 ----------
    def _build_behavior_tree(self) -> py_trees.behaviour.Behaviour:
        """
        构建行为树:
          Selector
          ├── AvoidRiskyTask  (valence<0 & arousal>0.6)
          ├── HighEnergyTask (valence>0.5 & arousal>0.5)
          ├── Confront       (dominance>0.7)
          └── Idle
        """
        def condition(fn):  # 装饰器生成 Condition Behavior
            class _Cond(py_trees.behaviour.Behaviour):
                def update(self_inner):
                    return py_trees.common.Status.SUCCESS if fn() else py_trees.common.Status.FAILURE
            return _Cond(fn.__name__)
        
        root = py_trees.composites.Selector("Root", memory=True)
        root.add_children([
            py_trees.composites.Sequence("AvoidRiskyTask", children=[
                condition(lambda: self.valence < 0 and self.arousal > 0.6),
                ActionNode("avoid_risky_tasks")
            ],
            memory=True),
            py_trees.composites.Sequence("HighEnergyTask", children=[
                condition(lambda: self.valence > 0.5 and self.arousal > 0.5),
                ActionNode("perform_task_with_high_energy")
            ],
            memory=True),
            py_trees.composites.Sequence("Confront", children=[
                condition(lambda: self.dominance > 0.7),
                ActionNode("confront_opponent")
            ],
            memory=True),
            ActionNode("idle")  # fallback
        ])
        return root

    def choose_action(self):
        """Tick 行为树并返回动作字符串"""
        self.decay_emotion()
        self.behavior_root.tick_once()
        # 叶子节点 ActionNode 会把所选 action 存到 self.last_action
        return getattr(self, "last_action", "idle")

class ActionNode(py_trees.behaviour.Behaviour):
    """简单动作节点，将动作名写到 agent.last_action"""
    def __init__(self, action_name: str):
        super().__init__(name=action_name)
        self.action_name = action_name
    def update(self):
        # parent pointer: self.parent.parent ... until agent
        agent = self.root.tip().blackboard.get('agent', None)
        if agent:
            agent.last_action = self.action_name
        return py_trees.common.Status.SUCCESS

# 示例用法
agent = EmotionalBehaviorAgent(name="Agent1", model_client=model_client)
agent.update_emotion('task_failed')
# agent.update_state('searching')
# action = agent.choose_action()
# print(f"Agent's emotional state: {agent.emotion}, action: {action}")
