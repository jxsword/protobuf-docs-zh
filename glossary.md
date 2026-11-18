# 术语表（glossary）

> 本表是全仓库唯一权威术语源：新词必须先入表再使用；术语变更仅对新翻译强制，
> 历史译文由 `tools/check_terms.py --fix` 可选批量回填（Phase 1 实现）。
>
> 译法底稿来源：
> - [gRPC 官方中文站](https://grpc.io.cn/)（grpc.io 中文版）的成熟译法；
> - Google 开发者中文（developers.google.cn）旧版 Protocol Buffers 文档惯例；
> - 社区既有博客型翻译（daobook/protobuf、tearwind 等项目）的通用用法。
>
> 表格约定：
> - 「英文」列可用 `;` 分隔同义写法；「中文」列为 `-` 表示**保留英文不翻译**；
> - 备注列含「保留」的条目同样视为保留英文；保留词在正文首次出现时可括注中文释义；
> - 非保留术语在译文首次出现时，须在括号内附英文原文（如「消息（message）」），
>   之后可直接使用中文译名——`check_terms.py` 以此形态为通过标准。

| 英文 | 中文 | 备注 |
| --- | --- | --- |
| Protocol Buffers; protobuf; Protobuf | - | 产品名保留英文 |
| proto2; proto3 | - | 语言版本名保留英文 |
| protoc | - | 编译器命令名保留英文 |
| gRPC | - | 产品名保留英文 |
| UTF-8 | - | 编码名保留英文 |
| codelab | - | 保留英文，可括注"代码实验教程" |
| syntax | syntax | 文件首行声明关键字保留；作普通名词时译"语法" |
| message | 消息 | |
| field | 字段 | |
| field name | 字段名 | |
| field number | 字段编号 | |
| tag | 标签 | 指二进制编码中的键 |
| scalar | 标量 | |
| enum | 枚举 | 关键字保留；作类型概念时译"枚举" |
| repeated | repeated | 关键字保留；概念可表述为"可重复字段" |
| optional | optional | 关键字保留 |
| required | required | 关键字保留（proto2） |
| map | map | 关键字保留；作概念时译"映射" |
| oneof | oneof | 关键字保留 |
| reserved | reserved | 关键字保留；作概念时译"保留（字段号/名）" |
| import | import | 关键字保留；作概念时译"导入" |
| public import | 公共导入 | |
| package | package | 关键字保留；作概念时译"包" |
| option; options | 选项 | `option` 声明关键字保留；概念译"选项" |
| extension | 扩展 | 含 proto2 extensions |
| service | 服务 | |
| RPC | RPC | 首次出现括注"远程过程调用（RPC）" |
| edition | 版次 | Editions 机制术语，与版本（version）严格区分 |
| version | 版本 | 指发布版本 |
| encoding | 编码 | |
| wire format | 线路格式 | 全仓统一此译法 |
| serialization | 序列化 | |
| deserialization | 反序列化 | |
| parse | 解析 | |
| schema | 模式 | |
| descriptor | 描述符 | |
| descriptor pool | 描述符池 | |
| reflection | 反射 | |
| varint | varint | 保留，首次出现括注"可变长度整数（varint）" |
| zigzag | zigzag | 保留，zigzag 编码 |
| packed | packed | 关键字保留；作概念时译"紧凑编码（packed）" |
| payload | 载荷 | |
| key | 键 | |
| value | 值 | |
| default value | 默认值 | |
| unknown fields | 未知字段 | |
| generated code | 生成代码 | |
| code generator | 代码生成器 | |
| plugin | 插件 | |
| runtime | 运行时 | |
| nested type | 嵌套类型 | |
| namespace | 命名空间 | |
| group | 组 | proto2 groups（已废弃特性） |
| well-known types | 知名类型 | |
| field presence | 字段存在性 | |
| explicit presence | 显式存在性 | |
| implicit presence | 隐式存在性 | |
| tracking | 追踪 | 如 presence tracking = 存在性追踪 |
| hasbit | hasbit | 保留 |
| arena | arena | 保留，指 C++ arena 内存分配机制 |
| string view | 字符串视图 | 对应 C++ string_view |
| backward compatibility | 向后兼容 | |
| forward compatibility | 向前兼容 | |
| breaking change | 破坏性变更 | |
| deprecation; deprecated | 弃用 | |
| release | 发布 | |
| release notes | 发布说明 | |
| feature | 特性 | |
| setting | 设置 | |
| cross-language | 跨语言 | |
| structured data | 结构化数据 | |
| language-neutral | 语言无关 | |
| platform-neutral | 平台无关 | |
| extensible | 可扩展 | |
| tutorial | 教程 | |
| style guide | 样式指南 | |
| language guide | 语言指南 | |
| accessor | 访问器 | |
| builder | 构建器 | |
| deterministic | 确定性 | 如确定性序列化 |
| canonical | 规范化 | |
| text format | 文本格式 | |
| binary format | 二进制格式 | |
| JSON mapping | JSON 映射 | |
| upstream | 上游 | |
| downstream | 下游 | |
| proto file; .proto file | proto 文件 | |
| overview | 概览 | 作页面标题时同样译"概览" |
| quick start | 快速开始 | |
| installation | 安装 | |
| downloads | 下载 | |

### Phase 1 批次新增（2026-11-19）

| 英文 | 中文 | 备注 |
| --- | --- | --- |
| singular | 单数 | 指字段基数（cardinality），译"单数字段（singular field）" |
| cardinality | 基数 | |
| wire type | 线路类型 | 二进制编码中的类型标记 |
| round-trip; round trip | 往返 | |
| self-delimiting | 自定界 | |
| length-delimited | 长度限定 | 长度前缀定界记录 |
| hazzer | hazzer | 保留，指设置 hasbit 的内联辅助方法 |
| enumerator | 枚举项 | enum 的取值成员 |
| no presence | 无存在性 | |
| presence discipline | 存在性规则 | |
| open enum; closed enum | - | 保留 enum；作概念译"开放式/封闭式枚举" |
| add-on | 附加组件 | 区别于 plugin=插件（编译器插件） |
| redact; redaction | 脱敏 | |
| retention | 保留性 | 指选项的 RETENTION 属性 |
| asset | 发布产物 | GitHub release 资产语境 |
| extension range | 扩展区间 | |
| deep clone | 深拷贝 | |
| map entry | 映射条目 | map 的线路格式承载消息 | |
