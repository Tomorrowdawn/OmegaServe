# OmegaServe 概述

OmegaServe 的设计目标是让基于 **OmegaConf/Hydra** 的程序以“配置即服务”的形式运行。通过动态切换配置即可切换服务行为，并提供保活、重启、端口发现等运行时能力。底层采用统一的子进程模型：无论通过 Python 接口还是 CLI，父进程都会 fork/启动一个子进程运行 Hydra 包裹的脚本，并通过环境变量传递运行时信息。

## 接口设计

### Python 接口
- `Service` 协议描述了服务签名：`__call__(config: DictConfig, runtime: Runtime)`。
- `serve_script(path, runtime, overrides=())`：直接以子进程方式运行 Hydra 脚本，等待其退出并返回退出码。
- `Runtime` 结构体（基于 `attrs`）持有 host、omega_port、service_port、日志路径、环境变量等运行时信息，作为服务执行上下文注入，默认 host 为 IPv6 友好的 `::`，存储时不带方框，在需要拼 URL 时再添加。`runtime_from_env` 允许直接从环境变量推导默认运行时。

### CLI 接口
`omgserve <runtime overrides> script.py <service hydra overrides>`

- `runtime overrides`：使用 `key=value` 形式快速覆盖运行时选项（如 `host=[::] omega_port=8080 service_port=10080`）。
- `script.py`：一个通过 `hydra.main` 包裹的 Hydra 程序，OmegaServe 通过共享的子进程启动器直接运行它。
- `service hydra overrides`：传递给 Hydra 的标准覆盖参数列表。

CLI 只负责参数解析，随后调用同一套子进程启动接口。运行时信息通过环境变量公开：`OMEGASERVE_HOST`、`OMEGASERVE_OMEGA_PORT` 与 `OMEGASERVE_SERVICE_PORT`。若配置了 `Runtime.log_path`，stdout/stderr 将被重定向到该文件。

#### CLI 示例

```bash
omgserve host=[::1] omega_port=9000 service_port=10000 app.py model.name=resnet
```

上述命令会在 IPv6 回环地址上运行控制平面，服务自身监听 `service_port=10000`，并将额外的 Hydra 覆盖参数传递给 `app.py`。由于 host 保留原始写法，若后续要拼接 URL，可在需要时自行加上方框。

## 核心能力规划

1. **配置驱动的重启**：接受 `DictConfig` 后决定是否重启服务，比较配置差异以避免不必要的重启。
2. **API 端点**：`/api/v1` 下暴露 `status`、`restart`、`ports`。
   - `status`：返回当前状态与可选配置快照。
   - `restart`：接收新的配置或 Hydra 覆盖，验证后触发重启（底层仍通过子进程重启脚本）。
   - `ports`：服务正常时返回 omega 服务与被托管服务的端口（`omega_port`、`service_port`）。
3. **运行时管理**：自动端口分配、stdout/stderr 日志记录、服务健康探测等逻辑将集成于 `ServiceController` 的具体实现中。

## 后续开发指引

- **框架选择**：API 层可以基于 FastAPI、Quart 或任何支持 ASGI 的框架实现；确保 `ServiceController` 的接口保持不变。
- **配置比较**：可以在 `StatusReport` 中携带当前配置哈希，结合 `RestartRequest` 对比差异决定是否重启。
- **守护与保活**：实现时建议将进程管理与日志收集分离，以保持 Unix 哲学中的简单性与可组合性。

## 发布与打包

- 使用 PEP 621 `pyproject.toml` 与 `setuptools` 构建，安装后提供 `omgserve` 可执行脚本。
- 核心依赖通过 `requirements.txt` 管理：`omegaconf`、`hydra-core`（用于覆盖解析）、`attrs`。

本仓库当前仅包含接口定义与最小实现，方便后续迭代时直接填充具体逻辑。
