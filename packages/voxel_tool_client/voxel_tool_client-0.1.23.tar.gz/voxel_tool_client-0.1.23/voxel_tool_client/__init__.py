import requests
import dataclasses
from typing import *

@dataclasses.dataclass()
class ClientConfig:
    base_url: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

@dataclasses.dataclass()
class Vector3:
    x: float
    y: float
    z: float

@dataclasses.dataclass()
class ResultData:
    data: Optional[Any] = None
    error: Optional[str] = None

@dataclasses.dataclass()
class NpcFindingRequest():
    npc_id: int
    world_id: int

@dataclasses.dataclass()
class NpcFindingResult():
    success: bool = False
    message: Optional[str] = None
    error: Optional[str] = None

    position: Optional[Vector3] = None

@dataclasses.dataclass()
class PathFindingRequest():
    world_id: int
    start: Vector3
    end: Vector3
    not_move: Optional[List[Vector3]] = None

@dataclasses.dataclass()
class PathFindingResult():
    success: bool = False
    message: Optional[str] = None
    error: Optional[str] = None

    path: Optional[List[Vector3]] = None
    collision: Optional[List[Vector3]] = None

@dataclasses.dataclass()
class GetNPCIdByWorldIdRequest():
    world_id: int

@dataclasses.dataclass()
class GetNPCIdByWorldIdResult():
    success: bool = False
    message: Optional[str] = None
    error: Optional[str] = None

    npc_ids: Optional[List[int]] = None

@dataclasses.dataclass()
class NpcFindingResult():
    success: bool = False
    message: Optional[str] = None
    error: Optional[str] = None

    position: Optional[Vector3] = None

class VoxelClient:
    """
    用于访问体素化服务器的客户端, 创建时需要初始化ClientConfig。
    base_url为体素化服务器的地址, username和password为体素化服务器的用户名和密码。
    
    使用示例:
    ```python
    base_url = "http://127.0.0.1:8000" # 体素化服务器的地址
    username = "123456" # 体素化服务器的用户名
    password = "123456" # 体素化服务器的密码
    world_id = 1 # 世界ID
    start = Vector3(x=0, y=0, z=0) # 起点坐标

    voxel_client = VoxelClient(ClientConfig(base_url=base_url, username=username, password=password))
    voxel_client.get_voxel_version()
    npc_ids = voxel_client.get_npc_id_by_world_id(GetNPCIdByWorldIdRequest(world_id=world_id)).npc_ids
    if npc_ids is not None:
        for npc_id in npc_ids:
            npc_position = voxel_client.find_npc_position(NpcFindingRequest(npc_id=npc_id, world_id=world_id))
            if npc_position.position is not None:
                path = voxel_client.find_path(PathFindingRequest(world_id=world_id, start=start, end=npc_position.position))
                if path.path is not None:
                    print(f"NPC {npc_id} 的坐标: {npc_position.position}")
                    print(f"NPC {npc_id} 的路径: {path.path}")
    ```
    """
    def __init__(self, config: ClientConfig):
        self.config = config

    def _get_default_config(self)-> Dict[str, Any]:
        return {
            "username": self.config.username,
            "password": self.config.password,
        }

    def _do_request(self, sub_url: str, params: Dict[str, Any]) -> ResultData:
        try:
            data = {
                "config": self._get_default_config(),
                "data": params
            }
            url = f"{self.config.base_url}{sub_url}"
            response = requests.post(url, json=data)
            response.raise_for_status()
            return ResultData(
                data=response.json(),
                error=None
            )
        except requests.exceptions.RequestException as e:
            return ResultData(
                data=None,
                error=f"请求失败: {str(e)}"
            )
        
    def get_voxel_version(self) -> Optional[str]:
        """
        获取体素化服务器的版本号，版本号中带有日期，可看到是什么时候生成的数据。
        """
        sub_url = "/get_voxel_version/"
        result = self._do_request(sub_url, {})
        if result.error is not None:
            return None
        data_version = result.data
        if isinstance(data_version, str) is False or data_version == "":
            return None
        return data_version

    """
    路径规划, 从起点到终点, 返回路径。

    输入参数:
    world_id: 世界ID
    start: 起点坐标
    end: 终点坐标

    输出参数:
    success: 是否成功
    message: 消息
    error: 错误信息
    path: 从起点到终点的路径
    collision: 碰撞点(返回过程中寻路过程中查询的碰撞点。TODO:需要服务器支持.)
    """
    def find_path(self, params: PathFindingRequest) -> PathFindingResult:
        data = dataclasses.asdict(params)
        if params.not_move is None:
            sub_url = "/path_finding/"
            data.pop("not_move")
        else:
            sub_url = "/path_finding_with_not_move/"
        result = self._do_request(sub_url, data)
        if result.error is not None:
            return PathFindingResult(   
                success=False,
                message=None,
                path=None,
                collision=None,
                error=result.error
            )

        path = None
        data_path = result.data.get("path")
        data_message = result.data.get("message")
        if data_path is not None:
            path = []
            for data_position in data_path:
                path_position = Vector3(x=data_position["x"], y=data_position["y"], z=data_position["z"])
                path.append(path_position)
        
        return PathFindingResult(
            success=True,
            message=data_message,
            path=path,
            collision=None,
            error=None,
        )
    
    """
    获取世界中NPC的ID

    输入参数:
    world_id: 世界ID
    
    输出参数:
    success: 是否成功
    message: 消息
    error: 错误信息
    npc_ids: 世界中NPC的ID列表
    """
    def get_npc_id_by_world_id(self, params: GetNPCIdByWorldIdRequest) -> GetNPCIdByWorldIdResult:
        sub_url = "/get_npc_id_by_world_id/"
        result = self._do_request(sub_url, dataclasses.asdict(params))
        if result.error is not None:
            return GetNPCIdByWorldIdResult(
                success=False,
                message=None,
                npc_ids=None,
                error=result.error,
            )
        data_npc_ids = result.data.get("npc_ids")
        if data_npc_ids is None:
            return GetNPCIdByWorldIdResult(
                success=False,
                message=None,
                npc_ids=None,   
                error=None,
            )
        npc_ids = []
        for data_npc_id in data_npc_ids:
            npc_ids.append(data_npc_id)
        return GetNPCIdByWorldIdResult(
            success=True,
            message=None,
            npc_ids=npc_ids,
            error=None,
        )

    def find_npc_position(self, params: NpcFindingRequest) -> NpcFindingResult:
        """
        获取NPC的坐标

        输入参数:
        npc_id: NPC的ID
        world_id: 世界ID 
        
        输出参数:
        success: 是否成功
        message: 消息
        error: 错误信息
        position: NPC的坐标
        """
        sub_url = "/find_npc_position/"
        result = self._do_request(sub_url, dataclasses.asdict(params))
        if result.error is not None:
            return NpcFindingResult(
                success=False,
                message=None,
                position=None,
                error=result.error,
            )
        data_position = result.data.get("position")
        data_message = result.data.get("message")
        position = None
        if data_position is not None:
            position = Vector3(x=data_position["x"], y=data_position["y"], z=data_position["z"])
        return NpcFindingResult(
            success=True,
            message=data_message,
            position=position,
            error=None,
        )