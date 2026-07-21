#!/usr/bin/env python3
"""
MA2026 - Command Line Tool for Minisoft Account 2026
Usage: ma2026.py <command> [options]
"""

import argparse
import sys
import json
import requests
import uuid

DEFAULT_SERVER = "http://uk.frp.one:20017"

def print_json(data):
    """打印格式化的 JSON"""
    print(json.dumps(data, indent=2, ensure_ascii=False))

def api_request(method, url, headers=None, json_data=None, timeout=10):
    """发送 API 请求并返回响应或错误信息"""
    try:
        resp = requests.request(method, url, headers=headers, json=json_data, timeout=timeout)
        return resp
    except Exception as e:
        print(f"请求错误: {e}", file=sys.stderr)
        sys.exit(1)

# ---------- 命令处理函数 ----------

def do_register(args):
    url = f"{args.server}/api/account/register"
    payload = {"username": args.username, "password": args.password}
    if args.email:
        payload["email"] = args.email
    resp = api_request("POST", url, json_data=payload)
    if resp.status_code == 201:
        print("注册成功")
    else:
        print(f"注册失败: {resp.status_code}")
        if resp.text:
            try:
                print_json(resp.json())
            except:
                print(resp.text)
        else:
            print("未知错误")

def do_login(args):
    url = f"{args.server}/api/account/login"
    payload = {"username": args.username, "password": args.password}
    resp = api_request("POST", url, json_data=payload)
    if resp.status_code == 200:
        data = resp.json()
        print("登录成功")
        print(f"Token: {data.get('token')}")
        if args.verbose:
            print("用户信息:")
            print_json(data.get('user', {}))
    else:
        print(f"登录失败: {resp.status_code}")
        try:
            print_json(resp.json())
        except:
            print(resp.text)

def do_profile(args):
    url = f"{args.server}/api/account/profile/{args.username}"
    headers = {"Authorization": f"Bearer {args.token}"}
    resp = api_request("GET", url, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        print("用户信息:")
        # 移除 devices 字段（如果存在）
        if 'devices' in data:
            del data['devices']
        print_json(data)
    else:
        print(f"获取资料失败: {resp.status_code}")
        try:
            print_json(resp.json())
        except:
            print(resp.text)

def do_totp_enable(args):
    url = f"{args.server}/api/account/totp/enable"
    headers = {"Authorization": f"Bearer {args.token}"}
    payload = {"username": args.username}
    resp = api_request("POST", url, headers=headers, json_data=payload)
    if resp.status_code == 200:
        data = resp.json()
        print("TOTP 密钥已生成")
        print(f"Secret: {data.get('secret')}")
        print(f"URI: {data.get('uri')}")
    else:
        print(f"启用 TOTP 失败: {resp.status_code}")
        try:
            print_json(resp.json())
        except:
            print(resp.text)

def do_totp_verify(args):
    url = f"{args.server}/api/account/totp/verify"
    payload = {"username": args.username, "code": args.code}
    resp = api_request("POST", url, json_data=payload)
    if resp.status_code == 200 and resp.json().get('valid'):
        print("TOTP 验证成功")
    else:
        print("TOTP 验证失败")

def do_change_password(args):
    url = f"{args.server}/api/account/change_password"
    payload = {
        "username": args.username,
        "old_password": args.old_password,
        "new_password": args.new_password
    }
    resp = api_request("POST", url, json_data=payload)
    if resp.status_code == 200:
        data = resp.json()
        print("密码修改成功")
        print(f"已撤销 {data.get('revoked_tokens', 0)} 个 token")
        print("提示:", data.get('note', ''))
    else:
        print(f"修改密码失败: {resp.status_code}")
        try:
            print_json(resp.json())
        except:
            print(resp.text)

def do_revoke_tokens(args):
    url = f"{args.server}/api/account/revoke_all_tokens"
    payload = {"username": args.username, "password": args.password}
    resp = api_request("POST", url, json_data=payload)
    if resp.status_code == 200:
        data = resp.json()
        print(f"已撤销 {data.get('revoked_count', 0)} 个 token")
    else:
        print(f"撤销 token 失败: {resp.status_code}")
        try:
            print_json(resp.json())
        except:
            print(resp.text)

def do_delete(args):
    url = f"{args.server}/api/account/delete"
    payload = {"username": args.username, "password": args.password}
    resp = api_request("POST", url, json_data=payload)
    if resp.status_code == 200:
        print("账户已永久删除")
    else:
        print(f"删除账户失败: {resp.status_code}")
        try:
            print_json(resp.json())
        except:
            print(resp.text)

def do_logout(args):
    url = f"{args.server}/api/account/logout"
    headers = {"Authorization": f"Bearer {args.token}"}
    resp = api_request("POST", url, headers=headers)
    if resp.status_code == 200:
        print("登出成功")
    else:
        print(f"登出失败: {resp.status_code}")
        try:
            print_json(resp.json())
        except:
            print(resp.text)

def main():
    parser = argparse.ArgumentParser(description="MA2026 Command Line Tool")
    parser.add_argument('--server', '-s', default=DEFAULT_SERVER,
                        help=f'服务器地址 (默认: {DEFAULT_SERVER})')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='显示详细信息')

    subparsers = parser.add_subparsers(dest='command', required=True,
                                       help='可用命令')

    # register
    p = subparsers.add_parser('register', help='注册新用户')
    p.add_argument('-u', '--username', required=True)
    p.add_argument('-p', '--password', required=True)
    p.add_argument('-e', '--email', help='邮箱（可选）')

    # login
    p = subparsers.add_parser('login', help='登录获取 token')
    p.add_argument('-u', '--username', required=True)
    p.add_argument('-p', '--password', required=True)

    # profile
    p = subparsers.add_parser('profile', help='查看用户信息')
    p.add_argument('-u', '--username', required=True)
    p.add_argument('-t', '--token', required=True)

    # totp-enable
    p = subparsers.add_parser('totp-enable', help='启用 TOTP')
    p.add_argument('-u', '--username', required=True)
    p.add_argument('-t', '--token', required=True)

    # totp-verify
    p = subparsers.add_parser('totp-verify', help='验证 TOTP 动态码')
    p.add_argument('-u', '--username', required=True)
    p.add_argument('-c', '--code', required=True, help='6位动态码')

    # change-password
    p = subparsers.add_parser('change-password', help='修改密码')
    p.add_argument('-u', '--username', required=True)
    p.add_argument('-o', '--old_password', required=True)
    p.add_argument('-n', '--new_password', required=True)

    # revoke-tokens
    p = subparsers.add_parser('revoke-tokens', help='撤销所有 token')
    p.add_argument('-u', '--username', required=True)
    p.add_argument('-p', '--password', required=True)

    # delete
    p = subparsers.add_parser('delete', help='永久删除账户')
    p.add_argument('-u', '--username', required=True)
    p.add_argument('-p', '--password', required=True)

    # logout
    p = subparsers.add_parser('logout', help='使当前 token 失效')
    p.add_argument('-t', '--token', required=True)

    args = parser.parse_args()

    # 分发命令
    commands = {
        'register': do_register,
        'login': do_login,
        'profile': do_profile,
        'totp-enable': do_totp_enable,
        'totp-verify': do_totp_verify,
        'change-password': do_change_password,
        'revoke-tokens': do_revoke_tokens,
        'delete': do_delete,
        'logout': do_logout,
    }
    cmd = args.command
    if cmd in commands:
        commands[cmd](args)
    else:
        print(f"未知命令: {cmd}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()