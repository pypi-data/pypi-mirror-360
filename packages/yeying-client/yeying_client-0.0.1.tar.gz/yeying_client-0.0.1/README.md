# yeying-client-python

## 打 whl 包命令

    python setup.py sdist bdist_wheel

## 发布公网

    # 安装 twine 命令
    pip install --upgrade twine setuptools wheel
    # 执行命令
    twine upload dist/*
    # 输入 token，自己注册 https://pypi.org 的账号，新建一个 token
    

## pytest 执行命令

    bash script/pytest.sh

## 资产仓库接口调用顺序

    ### 申请资产空间 / 使用现有的资产空间
    
        1: 创建资产仓库空间

        2: 获取到资产空间对应的 ID，后续文件上传 / 文件下载需要将其作为入参

    ### 文件上传接口调用

        1: cmd 命令方式调用

            # yeying_cmd put ${本地目录/本地文件} ${资产仓库空间 ID} ${身份文件-waresource.id} ${password}
            yeying_cmd put /Users/youxuehu/SDK/yeying-apps/yeying-client-python/.idea/ 96274d7e-0aae-4736-8f34-940a26f2f92a waresource.id 123456

        2: 代码调用

    ### 文件下载接口调用

        1: cmd 命令方式调用

            # yeying_cmd get ${资产仓库空间 ID} ${文件上传返回的 hash} ${本地文件输出路径}  ${身份文件-waresource.id} ${password}
            yeying_cmd get 96274d7e-0aae-4736-8f34-940a26f2f92a 55392b23b75e3a5e039232cce80f8b91ba6bf31d66057085afc6f522349c4281 xxxxxxx.tar.gz waresource.id 123456

        2: 代码调用

    ### 文件删除接口调用

        1: cmd 命令方式调用
            
            # yeying_cmd delete ${资产仓库空间 ID} ${文件上传返回的 hash} ${身份文件-waresource.id} ${password}
            yeying_cmd delete 96274d7e-0aae-4736-8f34-940a26f2f92a 55392b23b75e3a5e039232cce80f8b91ba6bf31d66057085afc6f522349c4281 waresource.id 123456

        2: 代码调用
    
    ### 文件复制

    ### 文件分享

    


