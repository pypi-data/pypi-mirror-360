# leafsdk/core/mission/mission_step.py
import traceback
from pymavlink import mavutil
from pymavlink.dialects.v20 import droneleaf_mav_msgs as leafMAV
from abc import ABC, abstractmethod
from  leafsdk.core.mission.trajectory import WaypointTrajectory, TrajectorySampler
import leafsdk.utils.mavlink_helpers as mav_helpers
import time

from petal_app_manager.plugins.base import Petal
from petal_app_manager.plugins.decorators import http_action, websocket_action
from petal_app_manager.proxies.localdb import LocalDBProxy
from petal_app_manager.proxies.external import MavLinkExternalProxy
from petal_app_manager.proxies.redis import RedisProxy


from typing import Dict, Any

from leafsdk import logger

class _MissionStep(ABC):
    @abstractmethod
    def __init__(self):
        self.result = True # Indicates the logical output of the step (mostly used for conditional steps)
        self.completed = False # Indicates if the step has been completed
        self.leaf_msg = None  # Placeholder for MAVLink messages, if needed
        self._exec_count = 0 # Counter to track how many times the step has been executed
        self._start_count = 0 # Counter to when the step was started

    @abstractmethod
    def execute_step(self, mav_proxy: MavLinkExternalProxy):
        raise NotImplementedError("Each subclass must implement `execute()`")

    @abstractmethod
    def to_dict(self) -> dict:
        raise NotImplementedError("Each subclass must implement `to_dict()`")
    
    @abstractmethod
    def log_info(self):
        raise NotImplementedError("Each subclass must implement `__str__()`")

    @classmethod
    @abstractmethod
    def from_dict(cls, params: dict):
        raise NotImplementedError("Each subclass must implement `from_dict()`")
    
    def execute(self, mav_proxy: MavLinkExternalProxy):
        if self._exec_count == 0:
            self.log_info()
        self.execute_step(mav_proxy=mav_proxy)
        self._exec_count += 1
        
        return self.result, self.completed


class __Goto(_MissionStep):
    def __init__(
            self, 
            mav_proxy: MavLinkExternalProxy = None,
            waypoints=None, 
            yaws_deg=None, 
            speed: float=2.0, 
            yaw_mode: str='lock', 
            cartesian: bool=False,
            **kwargs
        ):
        super().__init__()

        if waypoints is None and yaws_deg is None:
            raise ValueError("Either waypoints or yaws_deg must be provided.")
        if waypoints is not None and yaws_deg is not None:
            assert len(waypoints) == len(yaws_deg), \
                f"Expected {len(waypoints)} yaw values, got {len(yaws_deg)}"

        self.speed = speed
        self.yaws_deg = yaws_deg
        self.yaw_mode = yaw_mode
        self.cartesian = cartesian
        self.waypoints = waypoints
        self.target_waypoint = waypoints[-1]  # Last waypoint is the target
        self.yaw_offset = 0.0  # Default yaw offset
        self.waypoint_offset = [0.0, 0.0, 0.0]  # Default position offset
        self.__offset_pos_recved = False
        self.__offset_yaw_recved = False


        def handler_pos(msg: mavutil.mavlink.MAVLink_message) -> bool:
            self.waypoint_offset = [msg.x, msg.y, msg.z]
            self.__offset_pos_recved = True
            logger.info(f"Received external trajectory offset position: {self.waypoint_offset}")
            return True

        def handler_ori(msg: mavutil.mavlink.MAVLink_message) -> bool:
            self.yaw_offset = msg.z
            self.__offset_yaw_recved = True
            logger.info(f"Received external trajectory offset yaw: {self.yaw_offset}")
            return True
        
        self._handler_pos = handler_pos
        self._handler_ori = handler_ori

        if mav_proxy is not None:
            mav_proxy.register_handler(
                key=str(leafMAV.MAVLINK_MSG_ID_LEAF_EXTERNAL_TRAJECTORY_OFFSET_ENU_POS),
                fn=self._handler_pos
            )

            mav_proxy.register_handler(
                key=str(leafMAV.MAVLINK_MSG_ID_LEAF_EXTERNAL_TRAJECTORY_OFFSET_ENU_ORI),
                fn=self._handler_ori
            )
        else:
            logger.warning("MavLinkExternalProxy is not provided, external trajectory offsets will not be received.")


    def execute_step(self, mav_proxy: MavLinkExternalProxy = None):
        if not hasattr(self, 'trajectory_sampler'):
            # Compute the trajectory based on the waypoints and yaws
            if (self.__offset_pos_recved or self.__offset_yaw_recved):
                try:
                    self.compute_trajectory()
                    self._start_count = self._exec_count+1
                except Exception as e:
                    logger.error(f"❌ Error computing trajectory: {e}")
                    logger.error(traceback.format_exc())
                    raise e
        else:            
            if self._exec_count == self._start_count:
                if self.waypoints is not None:
                    if mav_proxy is not None:
                        msg = leafMAV.MAVLink_leaf_do_queue_external_trajectory_message(
                            target_system=mav_proxy.target_system,
                            queue=1,
                            traj_id=0 # 0 for position, 1 for yaw
                            )
                        mav_proxy.send(key='mav', msg=msg)
                        logger.info(f"ExternalTrajectoryPrimitive do queue command sent for position.")
                    else:
                        logger.warning("MavLinkExternalProxy is not provided, cannot send external trajectory messages.")

                if self.yaws_deg is not None:
                    if mav_proxy is not None:
                        msg = leafMAV.MAVLink_leaf_do_queue_external_trajectory_message(
                            target_system=mav_proxy.target_system,
                            queue=1,
                            traj_id=1 # 0 for position, 1 for yaw
                        )
                        mav_proxy.send(key='mav', msg=msg)
                        logger.info(f"ExternalTrajectoryPrimitive do queue command sent for yaw.")
                    else:
                        logger.warning("MavLinkExternalProxy is not provided, cannot send external trajectory messages.")
            else:
                position = [0, 0, 0]
                velocity = [0, 0, 0]
                acceleration = [0, 0, 0]
                yaw = 0.0
                yaw_rate = 0.0

                try:
                    if self.__offset_pos_recved:
                        t, position, velocity, acceleration = self.trajectory_sampler.sample_pos()
                    if self.__offset_yaw_recved:
                        t, yaw, yaw_rate = self.trajectory_sampler.sample_yaw()

                    if mav_proxy is not None:
                        msg = mav_helpers.create_msg_external_trajectory_setpoint_enu(
                            position_enu=position,
                            velocity_enu=velocity,
                            acceleration_enu=acceleration,
                            yaw=yaw,
                            yaw_rate=yaw_rate
                        )
                        mav_proxy.send(key='mav', msg=msg)
                    else:
                        logger.warning("MavLinkExternalProxy is not provided, cannot send external trajectory messages.")
                except StopIteration:
                    if mav_proxy is not None:
                        msg = leafMAV.MAVLink_leaf_do_terminate_external_trajectory_message(
                            target_system=mav_proxy.target_system,
                            status=1,
                            traj_id=0 # 0 for position, 1 for yaw
                        )
                        mav_proxy.send(key='mav', msg=msg)
                        msg = leafMAV.MAVLink_leaf_do_terminate_external_trajectory_message(
                            target_system=mav_proxy.target_system,
                            status=1,
                            traj_id=1
                        )
                        mav_proxy.send(key='mav', msg=msg)
                        logger.info(f"✅ Done: GotoGPSWaypoint to ({self.target_waypoint[0]}, {self.target_waypoint[1]}, {self.target_waypoint[2]})!")
                    else:
                        logger.warning("MavLinkExternalProxy is not provided, cannot send external trajectory messages.")

                    self.completed = True

                    # Unregister the handlers to stop receiving messages
                    if mav_proxy is not None:
                        logger.debug("Unregistering handlers for external trajectory offsets.")
                        mav_proxy.unregister_handler(
                            key=str(leafMAV.MAVLINK_MSG_ID_LEAF_EXTERNAL_TRAJECTORY_OFFSET_ENU_POS),
                            fn=self._handler_pos
                        )
                        mav_proxy.unregister_handler(
                            key=str(leafMAV.MAVLINK_MSG_ID_LEAF_EXTERNAL_TRAJECTORY_OFFSET_ENU_ORI),
                            fn=self._handler_ori
                        )
                

    def compute_trajectory(self):
        # Create a trajectory sampler based on the waypoints and yaws
        self.trajectory = WaypointTrajectory(
            waypoints=self.waypoints,
            yaws_deg=self.yaws_deg,
            speed=self.speed,
            home=self.waypoint_offset,
            home_yaw=self.yaw_offset,
            yaw_mode=self.yaw_mode,
            cartesian=self.cartesian
        )
        # self.trajectory.animate_projections_with_velocity()
        self.trajectory_sampler = TrajectorySampler(
            trajectory=self.trajectory,
        )

    def to_dict(self):
        return {
            "waypoints": self.waypoints,
            "yaws_deg": self.yaws_deg,
            "yaw_mode": self.yaw_mode,
            "speed": self.speed,
        }
    
    def log_info(self):
        logger.info(f"➡️ Executing Goto to ({self.target_waypoint[0]}, {self.target_waypoint[1]}, {self.target_waypoint[2]})")

    @classmethod
    def from_dict(cls, params: Dict[str, Any]) -> "__Goto":
        if any(key not in params for key in ["waypoints",]):
            logger.error("Missing required parameters for Goto.")
            raise ValueError("Missing required parameters: 'waypoints'.")

        # get required parameters
        args = {
            "waypoints": params.pop("waypoints"),
        }
        args.update(dict(params))

        return cls(**args)


class GotoGPSWaypoint(__Goto):
    def __init__(self, waypoints, mav_proxy: MavLinkExternalProxy=None, yaws_deg=None, speed: float=2.0, yaw_mode: str='lock'):
        super().__init__(waypoints=waypoints, mav_proxy=mav_proxy, yaws_deg=yaws_deg, speed=speed, yaw_mode=yaw_mode, cartesian=False)

    def log_info(self):
        logger.info(f"➡️ Executing GotoGPSWaypoint to ({self.target_waypoint[0]}, {self.target_waypoint[1]}, {self.target_waypoint[2]})")

class GotoLocalPosition(__Goto):
    def __init__(self, waypoints, mav_proxy: MavLinkExternalProxy=None, yaws_deg=None, speed: float=2.0, yaw_mode: str='lock'):
        super().__init__(waypoints=waypoints, mav_proxy=mav_proxy, yaws_deg=yaws_deg, speed=speed, yaw_mode=yaw_mode, cartesian=True)
    
    def log_info(self):
        logger.info(f"➡️ Executing GotoLocalPosition to ({self.target_waypoint[0]}, {self.target_waypoint[1]}, {self.target_waypoint[2]})")

class Takeoff(_MissionStep):
    def __init__(self, alt):
        super().__init__()
        self.alt = alt

    def execute_step(self, mav_proxy: MavLinkExternalProxy = None):
        if mav_proxy is not None:
            msg = leafMAV.MAVLink_leaf_do_takeoff_message(
                target_system=mav_proxy.target_system,
                altitude=self.alt
                )
            mav_proxy.send(key='mav', msg=msg)
        else:
            logger.warning("MavLinkExternalProxy is not provided, cannot send takeoff message.")

        self.completed = True

    def to_dict(self):
        return {"alt": self.alt}
    
    def log_info(self):
        logger.info(f"🛫 Executing Takeoff to altitude {self.alt}m")
    
    @classmethod
    def from_dict(cls, params: Dict[str, Any]) -> "__Goto":
        if any(key not in params for key in ["alt",]):
            logger.error("Missing required parameters for Takeoff.")
            raise ValueError("Missing required parameters: 'alt'.")

        # get required parameters
        args = {
            "alt": params.pop("alt"),
        }
        args.update(dict(params))

        return cls(**args)



class Wait(_MissionStep):
    def __init__(self, duration):
        super().__init__()
        self.duration = duration
        self.tick = 0 # Used to track the start time of the wait 

    def execute_step(self, mav_proxy: MavLinkExternalProxy = None):
        if self._exec_count == 0:
            self.tick = time.time()
        else:
            elapsed_time = time.time() - self.tick
            if elapsed_time >= self.duration:
                logger.info("✅ Done: Wait completed!")
                self.completed = True

    def to_dict(self):
        return {"duration": self.duration}
    
    def log_info(self):
        logger.info(f"⏲️ Executing Wait for {self.duration} seconds...")
    
    @classmethod
    def from_dict(cls, params: Dict[str, Any]) -> "__Goto":
        if any(key not in params for key in ["duration",]):
            logger.error("Missing required parameters for Wait.")
            raise ValueError("Missing required parameters: 'duration'.")

        # get required parameters
        args = {
            "duration": params.pop("duration"),
        }
        args.update(dict(params))

        return cls(**args)

class Land(_MissionStep):
    def __init__(self):
        super().__init__()

    def execute_step(self, mav_proxy: MavLinkExternalProxy = None):
        if mav_proxy is not None:
            msg = leafMAV.MAVLink_leaf_do_land_message(
                target_system=mav_proxy.target_system,
                )
            mav_proxy.send(key='mav', msg=msg)
        else:
            logger.warning("MavLinkExternalProxy is not provided, cannot send land message.")

        self.completed = True

    def to_dict(self):
        return {}
    
    def log_info(self):
        logger.info("🛬 Executing Land: Landing...")
    
    @classmethod
    def from_dict(cls, params):
        return cls(**params)


class Dummy(_MissionStep):
    def __init__(self, dummy=1):
        super().__init__()
        self.dummy = dummy

    def execute_step(self, mav_proxy: MavLinkExternalProxy = None):
        pass

    def to_dict(self):
        return {'dummy': self.dummy}
    
    def log_info(self):
        logger.info(f"➡️ Executing dummy!")
    
    @classmethod
    def from_dict(cls, params):
        return cls(**params)
    

def step_from_dict(step_type: str, params: dict, mav_proxy: MavLinkExternalProxy = None) -> _MissionStep:
    step_classes = {
        "Takeoff": Takeoff,
        "GotoGPSWaypoint": GotoGPSWaypoint,
        "GotoLocalPosition": GotoLocalPosition,
        "Wait": Wait,
        "Land": Land,
        "Dummy": Dummy,
        # Add more here
    }
    cls = step_classes.get(step_type)
    if cls is None:
        raise ValueError(f"Unknown mission_step type: {step_type}")
    if step_type in ["GotoGPSWaypoint", "GotoLocalPosition"]:
        # These steps require the mav_proxy to be passed
        params['mav_proxy'] = mav_proxy
    return cls.from_dict(params)