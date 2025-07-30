import requests
from runwayapi.response import LoginResponse
from typing import Optional, Dict
import random
import time
import os
import traceback
import urllib3
from requests.exceptions import ConnectionError, RequestException
from urllib3.exceptions import ProtocolError

# 用户代理配置
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"

# 内容类型映射
CONTENT_TYPE_MAP = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg', 
    '.png': 'image/png',
    '.gif': 'image/gif'
}

# 分辨率类型
RESOLUTION_MAP = {
    '16:9': (1920, 1088),  # 16:9 标准宽屏
    '21:9': (2112, 912),   # 21:9 超宽屏
    '4:3': (1456, 1088),   # 4:3 标准屏
    '1:1': (1088, 1088),   # 1:1 正方形
    '3:4': (1088, 1456),   # 3:4 竖屏
    '9:16': (1088, 1920)   # 9:16 手机屏幕
}

GEN4_RESOLUTION_MAP = {
    '16:9': (1280, 720),
    '9:16': (720, 1280)
}

# 最大重试次数
MAX_RETRIES = 3
# 重试间隔(秒)
RETRY_INTERVAL = 5

# Runway账号登录
def login(username: str, password: str) -> str:
    """
    调用 Runway API 进行登录并获取 token
    
    Args:
        username: 用户名
        password: 密码
        
    Returns:
        str: JWT token
        
    Raises:
        Exception: 当登录失败时抛出异常
    """
    print("Runway调用: 开始登录")
    url = "https://api.runwayml.com/v1/login"
    # 判断是否为邮箱
    if '@' in username:
        payload = {
            "email": username,
            "password": password,
            "machineId": None
        }
    else:
        payload = {
            "username": username,
            "password": password, 
            "machineId": None
        }

    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.post(url, json=payload, headers=headers)  # 使用model_dump代替dict
        response_data = response.json()
        
        if response.status_code != 200:
            print("Runway调用: 登录失败")
            return None

        login_response = LoginResponse(**response_data)
        print("Runway调用: 登录成功")
        return login_response.token
    except requests.exceptions.RequestException as e:
        print(f"Runway调用: 登录请求异常: {str(e)}")
        print(traceback.format_exc())
        return None
    except Exception as e:
        print(f"Runway调用: 登录发生错误: {str(e)}")
        print(traceback.format_exc())
        return None

# Runway 获取用户ID
def get_user_team_id(token: str) -> str:
    """
    获取Runway用户信息并返回状态码
    
    Args:
        token: JWT token
        
    Returns:
        int: 
            - 801: 账号已过期
            - 200: 账号正常
            
    Raises:
        Exception: 当请求失败时抛出异常
    """
    print("Runway调用: 开始获取用户ID")
    url = "https://api.runwayml.com/v1/profile"
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": USER_AGENT
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 401:
            print("Runway调用: 获取用户ID失败 - 未授权")
            return 401
        if response.status_code != 200:
            print("Runway调用: 获取用户ID失败")
            return None
        
        data = response.json()
        user_data = data["user"]
        
        # 检查账号是否过期
        print("Runway调用: 获取用户ID成功")
        return user_data['id']
        
    except requests.exceptions.RequestException as e:
        print(f"Runway调用: 获取用户ID请求异常: {str(e)}")
        print(traceback.format_exc())
        return None
    except Exception as e:
        print(f"Runway调用: 获取用户ID发生错误: {str(e)}")
        print(traceback.format_exc())
        return None
    
# 获取到用户任务数最小的SessionID
def get_min_session_id(token: str, team_id: str) -> str:
    """
    获取Runway会话列表并返回taskCount最小的会话ID
    
    Args:
        token: JWT token
        team_id: 团队ID
        
    Returns:
        str: taskCount最小的会话ID
        
    Raises:
        Exception: 当请求失败时抛出异常
    """
    print("Runway调用: 开始获取最小任务数会话ID")
    url = "https://api.runwayml.com/v2/sessions"
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": USER_AGENT
    }
    params = {
        "asTeamId": team_id,
        "limit": 50,
        "sortBy": "sortTimestamp",
        "orderBy": "DESC"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 401:
            print("Runway调用: 获取会话ID失败 - 未授权")
            return 401

        if response.status_code != 200:
            print("Runway调用: 获取会话ID失败")
            return None
            
        data = response.json()
        sessions = data.get("sessions", [])
        
        if not sessions:
            print("Runway调用: 未找到任何会话")
            return None
            
        # 找到taskCount最小的会话
        min_session = min(sessions, key=lambda x: x.get("taskCount", 0))
        
        print("Runway调用: 获取最小任务数会话ID成功")
        return min_session['id']
        
    except Exception as e:
        print(f"Runway调用: 获取会话ID发生错误: {str(e)}")
        print(traceback.format_exc())
        return None

# 获取到用户最近的50个Session
def get_sessions(token: str, team_id: str) -> list:
    """
    获取Runway会话列表并返回taskCount最小的会话ID
    
    Args:
        token: JWT token
        team_id: 团队ID
        
    Returns:
        str: taskCount最小的会话ID
        
    Raises:
        Exception: 当请求失败时抛出异常
    """
    print("Runway调用: 开始获取会话列表")

    # 百分之10的几率创建Session
    if random.random() < 0.1:
        print("Runway调用: 创建新会话")
        create_session(token, team_id)

    url = "https://api.runwayml.com/v2/sessions"
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": USER_AGENT
    }
    params = {
        "asTeamId": team_id,
        "limit": 50,
        "sortBy": "sortTimestamp",
        "orderBy": "DESC"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 401:
            print("Runway调用: 获取会话列表失败 - 未授权")
            return 401

        if response.status_code != 200:
            print("Runway调用: 获取会话列表失败")
            return None
            
        data = response.json()
        sessions = data.get("sessions", [])
        
        if not sessions:
            print("Runway调用: 未找到任何会话")
            return None
        
        print("Runway调用: 获取会话列表成功")
        return sessions
        
    except Exception as e:
        print(f"Runway调用: 获取会话列表发生错误: {str(e)}")
        print(traceback.format_exc())
        return None

# 创建session，返回SessionID
def create_session(token: str, team_id: str) -> str:
    """
    创建新的Runway会话
    
    Args:
        token: JWT token
        team_id: 团队ID
        
    Returns:
        str: 会话ID
        
    Raises:
        Exception: 当创建会话失败时抛出异常
    """
    print("Runway调用: 开始创建会话")
    url = "https://api.runwayml.com/v1/sessions"
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": USER_AGENT
    }
    payload = {
        "asTeamId": team_id,
        "taskIds": []
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 401:
            print("Runway调用: 创建会话失败 - 未授权")
            return 401

        if response.status_code != 200:
            print("Runway调用: 创建会话失败")
            return None
            
        data = response.json()
        session_data = data["session"]
        print("Runway调用: 创建会话成功")
        return session_data['id']
        
    except requests.exceptions.RequestException as e:
        print(f"Runway调用: 创建会话请求异常: {str(e)}")
        print(traceback.format_exc())
        return None
    except Exception as e:
        print(f"Runway调用: 创建会话发生错误: {str(e)}")
        print(traceback.format_exc())
        return None

# 获取assetGroupID，如果获取不到，则创建assetGroup
def get_asset_group_id(token: str, session_id: str, team_id: int) -> Optional[str]:
    """
    获取assetGroupId
    
    Args:
        session_id: 会话ID
        account: 账号信息
        
    Returns:
        str: 成功时返回assetGroupId，失败返回None
    """
    print("Runway调用: 开始获取资源组ID")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "User-Agent": USER_AGENT
        }
        
        response = requests.get(
            f"https://api.runwayml.com/v1/sessions/{session_id}",
            headers=headers,
            params={"asTeamId": team_id}
        )

        if response.status_code == 401:
            print("Runway调用: 获取资源组ID失败 - 未授权")
            return 401

        if response.status_code != 200:
            print("Runway调用: 获取资源组ID失败")
            return None
        
        data = response.json()        
        # 从session对象中获取assetGroupId
        asset_group_id = data.get('session', {}).get('assetGroupId')
        if asset_group_id:
            print("Runway调用: 获取资源组ID成功")
            return asset_group_id
        else:
            print("Runway调用: 未找到资源组ID，尝试创建新的资源组")
            return get_asset_group(token, session_id, team_id)  
    except Exception as e:
        print(f"Runway调用: 获取资源组ID发生错误: {str(e)}")
        print(traceback.format_exc())
        return None

# 获取assetGroupID，如果获取不到，则创建assetGroup
def get_asset_group(token: str, session_id: str, team_id: int) -> Optional[str]:
    """
    获取assetGroupId
    
    Args:
        session_id: 会话ID
        account: 账号信息
        
    Returns:
        str: 成功时返回assetGroupId，失败返回None
    """
    print("Runway调用: 开始创建资源组")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": USER_AGENT
    }
    
    response = requests.post(
        f"https://api.runwayml.com/v1/sessions/{session_id}/assetGroup",
        headers=headers,
        params={"asTeamId": team_id}
    )

    if response.status_code == 401:
        print("Runway调用: 创建资源组失败 - 未授权")
        return 401

    if response.status_code != 200:
        print("Runway调用: 创建资源组失败")
        return None
    
    data = response.json()        
    # 从assetGroup对象中获取id
    asset_group_id = data.get('assetGroup', {}).get('id')
    if asset_group_id:
        print("Runway调用: 创建资源组成功")
        return asset_group_id
    else:
        print("Runway调用: 创建资源组失败 - 未获取到ID")
        return None


# 生成图片
def generate_image(
    token: str,
    team_id: str,
    session_id: str,
    prompt: str,
    resolution: str = '9:16',
    num_images: int = 1,
    seed: int = random.randint(1, 1000000)
) -> list[str]:
    print("Runway调用: 开始生成图片")
    asset_group_id = get_asset_group_id(token, session_id, team_id)
    if not asset_group_id:
        print("Runway调用: 生成图片失败 - 未获取到资源组ID")
        return None
    width, height = RESOLUTION_MAP[resolution]
    # 准备正确的API请求参数
    payload={
        "taskType": "text_to_image",
        "internal": False,
        "options": {
            "text_prompt": prompt,
            "seed": seed,
            "exploreMode": True,
            "width": width,
            "height": height,
            "flip": True,
            "num_images": num_images,
            "diversity": 2,
            "name": f"Frames {prompt} a-2, {seed}",
            "assetGroupId": asset_group_id
        },
        "asTeamId": team_id,
        "sessionId": session_id
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": USER_AGENT
    }

    while True:
        try:
            if not is_can_generate_image(token, team_id):
                print("Runway调用: 等待生成图片权限...")
                time.sleep(1)
                continue

            response = requests.post(
                f"https://api.runwayml.com/v1/tasks",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 401:
                print("Runway调用: 生成图片失败 - 未授权")
                return 401
                
            if response.status_code == 429:
                print("Runway调用: 请求过于频繁，等待重试...")
                time.sleep(3)
                continue
                
            if response.status_code == 200:
                print("Runway调用: 创建图片生成任务成功")
                break
                
            time.sleep(3)
            
        except requests.exceptions.RequestException as e:
            print(f"Runway调用: 生成图片请求异常: {str(e)}")
            print(traceback.format_exc())
            return None
    
    data = response.json()
    task_id = data.get('task', {}).get('id')

    # 等待30S获取任务状态
    print("Runway调用: 等待图片生成完成...")
    time.sleep(30)

    urls = get_image_task_detail(token, team_id, task_id)
    if urls:
        print("Runway调用: 图片生成完成")
    else:
        print("Runway调用: 图片生成失败")

    return urls

def generate_video_for_gen4(
    token: str,
    team_id: str,
    session_id: str,
    image_url: str,
    prompt: str,
    second: int = 5,
    width: int = 1088,
    height: int = 1920,
    seed: int = random.randint(1, 4294967295)
) -> list[str]:
    print("Runway调用: 开始生成视频")
    model = "gen4_turbo"
    asset_group_id = get_asset_group_id(token, session_id, team_id)
    if not asset_group_id:
        print("Runway调用: 生成视频失败 - 未获取到资源组ID")
        return None

    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": USER_AGENT
    }

    if width > height:
        width = 1280
        height = 720
    else:
        width = 720
        height = 1280
    
    payload = {
        "taskType": model,
        "internal": False,
        "options": {
            "name": f"Gen-4 Turbo {seed}",
            "seed": seed,
            "route": "i2v",
            "exploreMode": True,
            "watermark": False,
            "width": width,
            "height": height,
            "seconds": second,
            "init_image": image_url,
            "flip": True,
            "assetGroupId": asset_group_id,
            "text_prompt": prompt
        },
        "asTeamId": team_id,
        "sessionId": session_id
    }

    while True:
        try:
            if not is_can_generate_video(token, team_id, model, second):
                print("Runway调用: 等待生成视频权限...")
                time.sleep(1)
                continue

            response = requests.post(
                f"https://api.runwayml.com/v1/tasks",
                headers=headers,
                json=payload
            )
            
            
            if response.status_code == 401:
                print("Runway调用: 生成视频失败 - 未授权")
                return 401
                
            if response.status_code == 429:
                print("Runway调用: 请求过于频繁，等待重试...")
                time.sleep(3)
                continue
            
            if response.status_code == 200:
                print("Runway调用: 创建视频生成任务成功")
                break
                
            time.sleep(3)
            
        except requests.exceptions.RequestException as e:
            print(f"Runway调用: 生成视频请求异常: {str(e)}")
            print(traceback.format_exc())
            return None
    
    data = response.json()
    task_id = data.get('task', {}).get('id')

    # 等待30S获取任务状态
    print("Runway调用: 等待视频生成完成...")
    time.sleep(30)

    urls = get_video_task_detail(token, team_id, task_id)
    if urls:
        print("Runway调用: 视频生成完成")
    else:
        print("Runway调用: 视频生成失败")

    return urls


# 生成视频
def generate_video_for_gen3a(
    token: str,
    team_id: str,
    session_id: str,
    image_url: str,
    prompt: str,
    second: int = 5,
    seed: int = random.randint(1, 4294967295)
) -> list[str]:
    print("Runway调用: 开始生成视频")
    model = "gen3a_turbo"
    asset_group_id = get_asset_group_id(token, session_id, team_id)
    if not asset_group_id:
        print("Runway调用: 生成视频失败 - 未获取到资源组ID")
        return None

    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": USER_AGENT
    }
    
    payload = {
        "taskType": model,
        "internal": False,
        "options": {
            "name": f"Gen-3 Alpha Turbo {seed}",
            "seed": seed,
            "exploreMode": True,
            "watermark": False,
            "enhance_prompt": True,
            "seconds": second,
            "keyframes": [
                {
                    "image": image_url,
                    "timestamp": 0
                }
            ],
            "text_prompt": prompt,
            "flip": True,
            "assetGroupId": asset_group_id
        },
        "asTeamId": team_id,
        "sessionId": session_id
    }

    while True:
        try:
            if not is_can_generate_video(token, team_id, model, second):
                print("Runway调用: 等待生成视频权限...")
                time.sleep(1)
                continue

            response = requests.post(
                f"https://api.runwayml.com/v1/tasks",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 401:
                print("Runway调用: 生成视频失败 - 未授权")
                return 401
                
            if response.status_code == 429:
                print("Runway调用: 请求过于频繁，等待重试...")
                time.sleep(3)
                continue
            
            if response.status_code == 200:
                print("Runway调用: 创建视频生成任务成功")
                break
                
            time.sleep(3)
            
        except requests.exceptions.RequestException as e:
            print(f"Runway调用: 生成视频请求异常: {str(e)}")
            print(traceback.format_exc())
            return None
    
    data = response.json()
    task_id = data.get('task', {}).get('id')

    # 等待30S获取任务状态
    print("Runway调用: 等待视频生成完成...")
    time.sleep(30)

    urls = get_video_task_detail(token, team_id, task_id)
    if urls:
        print("Runway调用: 视频生成完成")
    else:
        print("Runway调用: 视频生成失败")

    return urls
    
# 获取视频任务状态, 返回视频URL
def get_video_task_detail(token: str, team_id: str, task_id: str) -> Optional[Dict]:
    """
    获取任务详细信息
    
    Args:
        task_id: 任务ID
        
    Returns:
        Dict: 包含任务详细信息的字典，失败返回None
    """
    print("Runway调用: 开始获取视频任务状态")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": USER_AGENT
    }
    
    while True:
        try:
            response = requests.get(
                f"https://api.runwayml.com/v1/tasks/{task_id}",
                headers=headers,
                params={"asTeamId": team_id}
            )
            
            if response.status_code == 401:
                print("Runway调用: 获取视频任务状态失败 - 未授权")
                return 401

            if response.status_code != 200:
                print("Runway调用: 获取视频任务状态失败")
                return None
                
            data = response.json()
            task = data.get('task', {})
            status = task.get('status')
            if status is None:
                print("Runway调用: 获取视频任务状态失败 - 未获取到状态")
                return None

            # 任务完成且成功
            if status == 'SUCCEEDED' and task.get('artifacts'):
                artifact = task['artifacts'][0]
                url = artifact.get('url')
                print("Runway调用: 视频任务完成")
                return url
            # 任务失败或取消    
            if status in ['FAILED', 'CANCELLED']:
                print("Runway调用: 视频任务失败或被取消")
                return None
            # 任务仍在进行中,等待3秒后继续查询
            print("Runway调用: 视频任务进行中...")
            time.sleep(3)
            
        except requests.exceptions.RequestException as e:
            print(f"Runway调用: 获取视频任务状态请求异常: {str(e)}")
            print(traceback.format_exc())
            return None
        except Exception as e:
            print(f"Runway调用: 获取视频任务状态发生错误: {str(e)}")
            print(traceback.format_exc())
            return None

# 获取图片任务状态, 返回图片URL列表
def get_image_task_detail(token: str, team_id: str, task_id: str) -> list[str]:
    """
    获取任务详细信息
    
    Args:
        task_id: 任务ID
        
    Returns:
        Dict: 包含任务详细信息的字典，失败返回None
    """
    print("Runway调用: 开始获取图片任务状态")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": USER_AGENT
    }
    
    while True:
        try:
            response = requests.get(
                f"https://api.runwayml.com/v1/tasks/{task_id}",
                headers=headers,
                params={"asTeamId": team_id}
            )
            
            data = response.json()
            task = data.get('task', {})
            status = task.get('status')

            if response.status_code == 401:
                print("Runway调用: 获取图片任务状态失败 - 未授权")
                return 401

            if response.status_code != 200:
                print("Runway调用: 获取图片任务状态失败")
                return None

            if status is None:
                print("Runway调用: 获取图片任务状态失败 - 未获取到状态")
                return None

            # 任务完成且成功
            if status == 'SUCCEEDED' and task.get('artifacts'):
                artifacts = task['artifacts']
                urls = []
                for artifact in artifacts:
                    urls.append(artifact.get('url'))
                print("Runway调用: 图片任务完成")
                return urls
            # 任务失败或取消    
            if status in ['FAILED', 'CANCELLED']:
                print("Runway调用: 图片任务失败或被取消")
                return None
            # 任务仍在进行中,等待3秒后继续查询
            print("Runway调用: 图片任务进行中...")
            time.sleep(3)
            
        except Exception as e:
            print(f"Runway调用: 获取图片任务状态发生错误: {str(e)}")
            print(traceback.format_exc())
            return None

# 上传图片，获取图片链接
def upload_image(token: str, file_path: str) -> Optional[str]:
    """
    上传图片
    """
    print("Runway调用: 开始上传图片")
    try:
        file_name = os.path.basename(file_path)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT
        }
        payload = {
            "filename": file_name,
            "numberOfParts": 1,
            "type": "DATASET"
        }

        # 重试机制
        for retry in range(MAX_RETRIES):
            try:
                response = requests.post(
                    f"https://api.runwayml.com/v1/uploads",
                    headers=headers,
                    json=payload
                )

                if response.status_code == 401:
                    print("Runway调用: 上传图片失败 - 未授权")
                    return 401

                if response.status_code != 200:
                    print("Runway调用: 上传图片失败")
                    if retry < MAX_RETRIES - 1:
                        print(f"Runway调用: 第{retry + 1}次重试...")
                        time.sleep(RETRY_INTERVAL)
                        continue
                    return None

                data = response.json()
                upload_url = data['uploadUrls'][0]
                upload_id = data['id']

                file_ext = os.path.splitext(file_path)[1].lower()
                content_type = CONTENT_TYPE_MAP.get(file_ext, 'application/octet-stream')
                headers = {
                    "Accept": "*/*",
                    "Content-Type": content_type,
                    "sec-fetch-site": "cross-site",
                    "User-Agent": USER_AGENT
                }

                file_size = os.path.getsize(file_path)
                headers["Content-Length"] = str(file_size)

                with open(file_path, 'rb') as f:
                    response = requests.put(upload_url, data=f, headers=headers)
                    response.raise_for_status()

                    etag = response.headers.get('ETag')
                    url = etag.strip('"')
                    if url:
                        headers = {
                            "Authorization": f"Bearer {token}",
                            "Content-Type": "application/json",
                            "Accept": "application/json"
                        }
                        payload = {
                            "parts": [
                                {
                                    "PartNumber": 1,
                                    "ETag": url
                                }
                            ]
                        }
                        response = requests.post(
                            f"https://api.runwayml.com/v1/uploads/{upload_id}/complete",
                            headers=headers,
                            json=payload
                        )

                        if response.status_code == 401:
                            print("Runway调用: 完成上传失败 - 未授权")
                            return 401

                        if response.status_code != 200:
                            print("Runway调用: 完成上传失败")
                            if retry < MAX_RETRIES - 1:
                                print(f"Runway调用: 第{retry + 1}次重试...")
                                time.sleep(RETRY_INTERVAL)
                                continue
                            return None

                        data = response.json()
                        print("Runway调用: 上传图片成功")
                        return data.get('url')

                break

            except (ConnectionError, ProtocolError) as e:
                print(f"Runway调用: 连接错误: {str(e)}")
                if retry < MAX_RETRIES - 1:
                    print(f"Runway调用: 第{retry + 1}次重试...")
                    time.sleep(RETRY_INTERVAL)
                    continue
                print(traceback.format_exc())
                return None

            except RequestException as e:
                print(f"Runway调用: 请求异常: {str(e)}")
                if retry < MAX_RETRIES - 1:
                    print(f"Runway调用: 第{retry + 1}次重试...")
                    time.sleep(RETRY_INTERVAL)
                    continue
                print(traceback.format_exc())
                return None

    except Exception as e:
        print(f"Runway调用: 上传图片发生错误: {str(e)}")
        print(traceback.format_exc())
        return None

# 检查是否可以生成图片
def is_can_generate_image(token: str, team_id: str) -> bool:
    """
    检查是否可以生成图片
    """
    print("Runway调用: 检查图片生成权限")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": USER_AGENT
    }
    payload = {
        "feature": "text_to_image",
        "count": 1,
        "asTeamId": team_id,
        "taskOptions": {
            "width": 0,
            "height": 0,
            "num_images": 4
        }
    }
    response = requests.post(
        "https://api.runwayml.com/v1/billing/estimate_feature_cost_credits",
        headers=headers,
        json=payload
    )
    if response.status_code == 401:
        print("Runway调用: 检查图片生成权限失败 - 未授权")
        return 401
    if response.status_code != 200:
        print("Runway调用: 检查图片生成权限失败")
        return None
    data = response.json()
    result = data.get('canUseExploreMode')
    if result:
        print("Runway调用: 有图片生成权限")
    else:
        print("Runway调用: 无图片生成权限")
    return result

# 检查是否可以生成视频,模型分类
def is_can_generate_video(
        token: str, 
        team_id: str,
        model: str,
        second: int) -> bool:
    """
    检查是否可以生成视频
    """
    print("Runway调用: 检查视频生成权限")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": USER_AGENT
    }
    payload = {
        "feature": model,
        "count": 1,
        "asTeamId": team_id,
        "taskOptions": {
            "seconds": second
        }
    }
    response = requests.post(
        "https://api.runwayml.com/v1/billing/estimate_feature_cost_credits",
        headers=headers,
        json=payload
    )
    if response.status_code == 401:
        print("Runway调用: 检查视频生成权限失败 - 未授权")
        return 401
    if response.status_code != 200:
        print("Runway调用: 检查视频生成权限失败")
        return None
    data = response.json()
    result = data.get('canUseExploreMode')
    if result:
        print("Runway调用: 有视频生成权限")
    else:
        print("Runway调用: 无视频生成权限")
    return result