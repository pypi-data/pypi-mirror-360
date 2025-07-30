# leafsdk/core/mission/mission_plan.py

import sys, time
import os
import json
import traceback
import networkx as nx
import matplotlib.pyplot as plt
from leafsdk import logger
# Add pymavlink to path
from petal_app_manager.proxies.external import MavLinkExternalProxy
from leafsdk.core.mission.mission_step import _MissionStep, step_from_dict

class MissionPlan:
    def __init__(self, mav_proxy: MavLinkExternalProxy = None, name: str="UnnamedMission"):
        self.name = name
        self.__info = {}
        self.__validated = False
        self.__mav_proxy = mav_proxy
        self.__graph = nx.MultiDiGraph()
        self.__current_node = None
        self.__head_node = None
        self.__last_added_node = None

    def add(self, to_name: str, to_step: _MissionStep, from_name: str=None, condition=None):
        first_node = not self.__graph.nodes
        self.add_step(to_name, to_step)
        if first_node:
            self.set_start(to_name)
        if from_name:
            self.add_transition(from_name, to_name, condition)
        elif self.__last_added_node:
            self.add_transition(self.__last_added_node, to_name, condition)
        self.__last_added_node = to_name

    def add_step(self, name: str, step: _MissionStep):
        if name in self.__graph:
            raise ValueError(f"Node name '{name}' already exists in mission plan '{self.name}'.")
        self.__graph.add_node(name, step=step)

    def add_transition(self, from_step: str, to_step: str, condition=None):
        self.__graph.add_edge(from_step, to_step, condition=condition, key=None)

    def set_start(self, name: str):
        if name not in self.__graph:
            raise ValueError(f"Start node '{name}' not found in mission graph.")
        self.__current_node = name
        self.__head_node = name

    def run_step(self):
        if self.__current_node is None:
            logger.info("✅ Mission complete.")
            return False

        step: _MissionStep = self.__graph.nodes[self.__current_node]['step']
        if step._exec_count == 0:
            step.feed_info(self.__info)
            logger.info(f"➡️ Executing step: {self.__current_node}")

        try:
            result, completed, self.__info = step.execute(mav_proxy=self.__mav_proxy)
        except Exception as e:
            logger.error(f"❌ Step {self.__current_node} failed: {e}\n{traceback.format_exc()}")
            self.__current_node = None
            return False
        
        if completed:
            next_node = None
            for successor in self.__graph.successors(self.__current_node):
                condition = self.__graph.edges[self.__current_node, successor, 0].get("condition")
                if condition is None or condition == result:
                    next_node = successor
                    break
            self.__current_node = next_node

        return True

    def add_subplan(self, subplan, prefix: str, connect_from: str=None, condition=None):
        if connect_from is None:
            connect_from = self.__last_added_node
        renamed_nodes = {}
        for name, data in subplan.__graph.nodes(data=True):
            new_name = f"{prefix}_{name}"
            self.__graph.add_node(new_name, **data)
            renamed_nodes[name] = new_name

        for u, v, edata in subplan.__graph.edges(data=True):
            self.__graph.add_edge(renamed_nodes[u], renamed_nodes[v], **edata)

        self.add_transition(connect_from, renamed_nodes[subplan.__head_node])
    
    def save(self, filepath: str):
        self.__validate()
        data = {
            "nodes": [
                {
                    "name": name,
                    "type": step.__class__.__name__,
                    "params": step.to_dict()
                }
                for name, step in self.__get_steps()
            ],
            "edges": [
                {"from": u, "to": v, "condition": self.__graph.edges[u, v, k].get("condition")}
                for u, v, k in self.__graph.edges
            ]
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"✅ MissionPlan file exported to: {filepath}")

    def load_from_dict(self, mission_graph: dict):
        self.__graph.clear()
        for i, node in enumerate(mission_graph["nodes"]):
            step = step_from_dict(node["type"], node["params"], mav_proxy=self.__mav_proxy)
            self.add_step(node["name"], step)
            if i == 0:
                self.set_start(node["name"])

        for edge in mission_graph["edges"]:
            self.add_transition(edge["from"], edge["to"], edge.get("condition"))
        
        logger.info(f"✅ MissionPlan is loaded.")

    def load_from_json(self, filepath: str):
        with open(filepath, "r") as f:
            data = json.load(f)

        self.__graph.clear()
        for i, node in enumerate(data["nodes"]):
            step = step_from_dict(node["type"], node["params"], mav_proxy=self.__mav_proxy)
            self.add_step(node["name"], step)
            if i == 0:
                self.set_start(node["name"])

        for edge in data["edges"]:
            self.add_transition(edge["from"], edge["to"], edge.get("condition"))
        
        logger.info(f"✅ MissionPlan file loaded from: {filepath}")

    def export_dot(self, filepath: str):
        try:
            from networkx.drawing.nx_pydot import write_dot
        except ImportError:
            logger.error("❌ pydot or pygraphviz is required to export DOT files. Please install via pip.")

        # Add 'label' attributes to edges using the 'condition' attribute
        for u, v, data in self.__graph.edges(data=True):
            if 'condition' in data:
                condition = data['condition']
                data['label'] = str(condition) if condition is not None else ''

        write_dot(self.__graph, filepath)
        logger.info(f"✅ DOT file exported to: {filepath}")

    def prepare(self):
        self.__validate()

    def __get_steps(self):
        for name, data in self.__graph.nodes(data=True):
            yield name, data['step']

    def __validate(self):
        errors = []
        for node in self.__graph.nodes:
            successors = list(self.__graph.successors(node))
            if len(successors) > 1:
                seen_conditions = set()
                for succ in successors:
                    edge_data = self.__graph.get_edge_data(node, succ)
                    condition = edge_data[0].get("condition")
                    if condition is None:
                        errors.append(f"Missing condition for edge {node} → {succ}")
                    elif condition in seen_conditions:
                        errors.append(f"Duplicate condition '{condition}' for branching at {node}")
                    else:
                        seen_conditions.add(condition)

        if errors:
            for e in errors:
                logger.error(f"❌ [prepare] {e}")
            raise ValueError("Mission plan validation failed. See errors above.")
        else:
            self.__validated = True
            logger.info("✅ Mission plan has been validated.")