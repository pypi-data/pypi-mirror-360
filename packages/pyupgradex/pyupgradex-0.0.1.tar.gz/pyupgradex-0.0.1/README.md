## 使用说明

pyupgradex 提供了一个命令行工具，支持以下子命令：

### plugins
列出所有注册的插件模块名称。

```bash
python -m pyupgradex plugins
```

### run
运行 pyupgrade，并支持禁用指定插件。

```bash
python -m pyupgradex run --disable-plugins plugin_name1 plugin_name2 -- other_args
```

`--disable-plugins` 参数用于禁用指定的插件，`other_args` 是传递给 pyupgrade 的额外参数。
