# requests.get() 同步的代码 -> 异步操作aiohttp
# pip install aiohttp

# ---异步协程下载三张图片
import asyncio
import aiohttp
import time
import aiofiles


async def aiodownload(url):
    """
    定义单个下载的协程函数
    @param url:
    @return:
    """

    # 发送请求.
    # 得到图片内容
    # 保存到文件
    name = url.rsplit("/", 1)[1]  # 从右边切, 切一次. 得到[1]位置的内容
    # async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=64,ssl=False)) as session:  # 不这样改下载不了
    async with aiohttp.ClientSession() as session:  # requests
        async with session.get(url, ssl=False) as resp:  # 对应于resp = requests.get(),ssl=false是为了避免出现ssl验证错误
            # 请求回来了. 写入文件
            # 可以自己去学习一个模块, aiofiles
            async with aiofiles.open(f"fig/{name}", mode="wb") as f:  # 创建文件
                await f.write(await resp.content.read())  # 读取内容是异步的. 需要await挂起, 读取文本用resp.text()

    print(name, "搞定")


async def main():
    """
    建立协程对象任务列表，别忘了把列表放入asyncio.wait()中
    @return:
    """
    tasks = []
    urls = [
        "http://kr.shanghai-jiuxin.com/file/2020/1031/191468637cab2f0206f7d1d9b175ac81.jpg",
        "http://kr.shanghai-jiuxin.com/file/2020/1031/563337d07af599a9ea64e620729f367e.jpg",
        "http://kr.shanghai-jiuxin.com/file/2020/1031/774218be86d832f359637ab120eba52d.jpg"
    ]
    # 添加下载任务
    for url in urls:
        task = asyncio.create_task(aiodownload(url))
        tasks.append(task)

    # 等待所有任务下载完成
    await asyncio.wait(tasks)


if __name__ == '__main__':
    t1 = time.time()
    # 运行异步协程任务
    asyncio.run(main())
    t2 = time.time()
    print("下载完毕。", '耗时', str(t2 - t1) + 's')
