# -*- coding:utf-8 -*-
"""
资产仓库 cmd client
支持本地资产上传
支持下载服务端资产
"""
import argparse
import ast
import os.path
from yeying.api.asset import asset_pb2
from yeying.api.web3 import Identity, SecurityAlgorithm
from yeying.client.downloader import DownloadResult
from yeying.client.model.file import File
from yeying.client.model.option import ProviderOption
from yeying.client.provider.asset_provider import AssetProvider
from yeying.client.tool.identity_service import load, decrypt_block_address
from yeying.client.uploader import UploadResult
from yeying.client import uploader, downloader
from google.protobuf.json_format import MessageToJson


def arg_parse():
    parser = argparse.ArgumentParser(description="Yeying warehouse cli")
    sub_parser= parser.add_subparsers(dest="command")

    # 上传本地资源
    put_parser = sub_parser.add_parser("put", help="上传资源")
    # proxy 参数可选，默认连接本地服务
    put_parser.add_argument(dest="proxy", help="envoy proxy address (optional), default value http://localhost:8641", nargs="?", default="http://localhost:8641")
    put_parser.add_argument(dest="source", help="local file path")
    put_parser.add_argument(dest="namespace_id", help="namespace_id")
    # encrypted 是否需要加密
    put_parser.add_argument(dest="encrypted", help="is encrypted")
    put_parser.add_argument(dest="identity_file", help="identity file")
    put_parser.add_argument(dest="password", help="password")


    # 下载服务端资源
    get_parser = sub_parser.add_parser("get", help="下载资源")
    # proxy 参数可选，默认连接本地服务
    get_parser.add_argument(dest="proxy", help="envoy proxy address (optional), default value http://localhost:8641", nargs="?", default="http://localhost:8641")
    get_parser.add_argument(dest="namespace_id", help="namespace_id")
    get_parser.add_argument(dest="hash", help="hash")
    get_parser.add_argument(dest="output", help="local file out path")
    get_parser.add_argument(dest="identity_file", help="identity file")
    get_parser.add_argument(dest="password", help="password")


    # 删除服务端资源
    delete_parser = sub_parser.add_parser("delete", help="删除资源")
    # proxy 参数可选，默认连接本地服务
    delete_parser.add_argument(dest="proxy", help="envoy proxy address (optional), default value http://localhost:8641", nargs="?", default="http://localhost:8641")
    delete_parser.add_argument(dest="namespace_id", help="namespace_id")
    delete_parser.add_argument(dest="hash", help="hash")
    delete_parser.add_argument(dest="identity_file", help="identity file")
    delete_parser.add_argument(dest="password", help="password")


    args = parser.parse_args()
    return args, parser


def package_dir(path):
    import uuid
    dst = "/tmp/%s.tar.gz" % str(uuid.uuid1().hex)[:8]
    cmd = "mkdir -p /tmp; tar -czf {dst} {src}".format(src=path, dst=dst)
    os.system(cmd)
    return dst


def upload(args, option, algorithm: SecurityAlgorithm):
    print("start upload")
    print(args)

    def upload_callback(result: UploadResult) -> None:
        print(f"[文件上传回调] 进度: {result['progress']['completed']}/{result['progress']['total']}")
        print(f"[文件上传回调] 区块namespaceId: {result['block'].namespaceId}")
        print(f"[文件上传回调] 区块大小: {result['block'].size} 字节")
        print(f"[文件上传回调] 区块哈希: {result['block'].hash}")
        print("-" * 40)

    if not os.path.exists(args.source):
        print("Invalid path %s" % args.source)
    else:
        path = args.source
        if os.path.isdir(path):
            print("packaging folder %s" % path)
            path = package_dir(path)
            print("packaging folder temp file %s" % path)
        upload_client = uploader.Uploader(option, algorithm)
        file = File(name=os.path.basename(path), size=os.stat(path).st_size, stream=path, last_modified=int(os.stat(path).st_mtime * 1000))
        res: asset_pb2.SignAssetResponse = upload_client.put(namespace_id=args.namespace_id, file=file, encrypted=ast.literal_eval(args.encrypted), block_callback=upload_callback)
        asset = res.body.asset
        print(f"upload success. asset={MessageToJson(asset)}")


def download(args, option, algorithm: SecurityAlgorithm):
    print("start download")
    print(args)
    download_client = downloader.Downloader(option, algorithm)
    namespace_id = args.namespace_id
    chunk_files = []
    def download_callback(result: DownloadResult) -> None:
        print(f"[文件下载回调] 进度: {result['progress']['completed']}/{result['progress']['total']}")
        print(f"[文件下载回调] 区块namespaceId: {result['block'].namespaceId}")
        print(f"[文件下载回调] 区块大小: {len(result['data'])} 字节")
        print(f"[文件下载回调] 区块哈希: {result['block'].hash}")
        chunk_files.append(result['data'])
        print("-" * 40)
    asset = download_client.get(namespace_id=namespace_id, _hash=args.hash, block_callback=download_callback)

    def merge_files(chunks, output_path):
        """合并分块文件为完整文件"""
        with open(output_path, 'wb') as output:
            for chunk in chunks:
                output.write(chunk)
        print(f"文件已合并至: {output_path}")

    merge_files(chunk_files, args.output)
    print(f"download success. asset={MessageToJson(asset)}")


def get_proxy(args):
    return args.proxy if args.proxy else os.getenv("SERVICE_PROXY_ADDRESS", "http://localhost:8641")


def delete(args, option):
    print("start delete")
    print(f"namespace_id={args.namespace_id}")
    print(f"hash={args.hash}")
    print(f"proxy={option.proxy}")
    delete_client = AssetProvider(option=option)
    response: asset_pb2.DeleteAssetResponse = delete_client.delete(args.namespace_id, args.hash)
    print(f"delete success. code={response.body.status.code}")


def main():
    args, parser = arg_parse()
    identity_file = args.identity_file
    if not os.path.exists(identity_file):
        raise Exception(f"identity_file not exists {identity_file}")

    identity: Identity = load(identity_file)
    block_address = decrypt_block_address(identity.blockAddress, identity.securityConfig.algorithm, args.password)
    print(f"block_address={block_address}")
    option = ProviderOption(
        proxy=get_proxy(args),
        block_address=block_address
    )
    if args.command == "put":
        upload(args, option, identity.securityConfig.algorithm)
    elif args.command == "get":
        download(args, option, identity.securityConfig.algorithm)
    elif args.command == "delete":
        delete(args, option)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
