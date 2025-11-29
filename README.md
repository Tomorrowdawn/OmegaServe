# OmegaServe

OmegaServe 提供“配置即服务”的接口定义，围绕 OmegaConf/Hydra 生态快速托管服务。当前版本侧重于公开可扩展的协议和 CLI 约定，便于后续填充具体实现。

## 特性
- `Service` 协议：统一的 Python 服务入口，接收 `DictConfig` 与 `Runtime`。
- `Runtime`：使用 `attrs` 定义的运行时上下文，包括 host、omega_port、service_port、日志路径等。
- CLI：`omgserve <runtime overrides> script.py <service hydra overrides>`，通过统一的子进程启动器运行 Hydra 包裹的服务进程。
- API 设计：`ServiceController` 约定 `status`、`restart`、`ports`（omega_port + service_port）等端点行为。

## 子进程执行

无论是 CLI 还是 Python 接口，底层都运行在“父进程监听 + 子进程执行”的模型上：

- Python 接口的 `serve` 会先获取运行时（默认从环境变量读取），再 fork 子进程执行 `Service`，父进程等待子进程退出。
- CLI 解析完参数后也使用同一套进程管理函数启动 Hydra 脚本，日志（如果设置了 `Runtime.log_path`）重定向到文件。

`Runtime` 会以环境变量的形式传递 `OMEGASERVE_HOST`、`OMEGASERVE_OMEGA_PORT`、`OMEGASERVE_SERVICE_PORT` 等信息，默认 host 为 IPv6 友好的 `::`，保持不加方框的原始写法，在需要拼接 URL 时再自行添加方框。

Python 环境下，可直接调用 `serve_script("service.py", runtime)` 以同样方式启动服务。

## 文档
请查看 [docs/overview.md](docs/overview.md) 获取接口与未来架构规划。
