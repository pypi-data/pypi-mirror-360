## 钻石铲命令行调用办法


在[安装](install.md)完钻石铲后，可以在命令行中通过`diamond-shovel`命令调用钻石铲。


#### 参数

`--plugin <插件包文件位置>`: 自动安装插件, 你也可以直接使用`cp`命令替代, 默认情况下会安装到`${cwd}/plugins/`下

`--target <公司名>`: 以该公司为目标执行自动化的安全审计任务, 可后接多个公司名, 可与`--ip`, `--domain`参数同用

`--ip <IP地址>`: 以该IP为目标执行自动化的安全审计任务, 可后接多个IP地址, 可与`--domain`, `--target`参数同用

`--domain <域名>`: 以该域名为目标执行自动化的安全审计任务, 可后接多个域名, 可与`--ip`, `--target`参数同用

`--json <json文件>`: 从json文件中读取所有目标

`--out-json <json文件>`: 将结果输出到json, 默认会输出到`./diamond-shovel-result.json`下

`--enable-plugin <插件名>`: 指定启用插件, 不可与`--disable-plugin`联用

`--disable-plugin <插件名>`: 指定禁用插件, 不可与`--enable-plugin`联用

不提供任何目标时将会将帮助信息以json格式输出到`--out-json`指定的文件中，默认是`/dev/stdout`也就是你正在看着的控制台


#### 使用🌰

样例输入:

```bash
diamond-shovel --enable-plugin fingerprinter -m www.baidu.com
```

样例输出(diamond-shovel-result.json):

```json
{
    "fingerprinter:worker.handle_task": []
}
```

其中`fingerprinter:worker.handle_task`中表示插件所注册的处理器, 值为处理器的返回值.
