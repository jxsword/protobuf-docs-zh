

+++
title = "我们更倾向于用扩展而非 Any"
weight = 93
description = "说明 Protobuf 团队为何后悔用 Any 取代扩展，以及为什么在大多数用例中更倾向于使用扩展"
type = "docs"
source_url = "https://protobuf.dev/design-decisions/extensions-over-any/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

proto3 推出时，移除了通用的[扩展（extension）](/programming-guides/editions#extensions)机制（仅保留自定义选项所用的扩展），并引入 [`google.protobuf.Any`](/programming-guides/editions#any) 作为其替代。

遗憾的是，`Any` 存在足够多的设计缺陷，以至于 Protobuf 团队对这一决定感到后悔。我们没有任何正式弃用（deprecate）`Any` 的计划，它也仍然受支持，但我们建议在几乎所有用例中用扩展代替 `Any`。

*   [Protobuf 版次（Editions）](/editions/overview) 自 2023 版次起恢复了对扩展的完整支持。
*   对于新的模式（schema），只要扩展能够满足用例，就**优先使用扩展而非 `Any`**（参见 [Proto 最佳实践](/best-practices/dos-donts#avoid-any)）。
*   将 `Any` 留给不常见的场景：横向基础设施需要传递完全任意的消息，而为每种可能的类型都声明一个扩展并不可行。

## 扩展与 `Any` 是什么 {#what}

这两种机制解决的都是同一个依赖问题：让容器消息（message）能够携带一个其 `.proto` 文件未被容器导入的子消息（submessage）。容器不必依赖每一种可能的载荷（payload）类型，而是由每种载荷去依赖容器。

### 扩展 {#what-extensions}

[扩展](/programming-guides/editions#extensions)是定义在其容器消息之外的字段（field），它使用容器通过 `extensions` 区间保留的字段编号（field number）：

```proto
// 文件 media/user_content.proto
edition = "2024";

package media;

message UserContent {
  string id = 1;

  extensions 100 to 199 [
    declaration = {
      number: 100,
      full_name: ".kittens.kitten_video",
      type: ".kittens.Video"
    }
  ];
}
```

```proto
// 文件 kittens/video_ext.proto
edition = "2024";

package kittens;

import "kittens/video.proto";
import "media/user_content.proto";

extend media.UserContent {
  Video kitten_video = 100;
}
```

在生成代码（generated code）中，扩展以类型化子消息的形式来访问，这个子消息直接存储在父消息上：

```cpp
media::UserContent content;
content.MutableExtension(kittens::kitten_video)->set_title("Cute kittens");

if (content.HasExtension(kittens::kitten_video)) {
  const kittens::Video& video = content.GetExtension(kittens::kitten_video);
}
```

在线路上，扩展与具有相同字段编号、类型和基数（cardinality）的常规字段完全相同。借助[扩展声明](/programming-guides/extension_declarations)，容器可以在一处列出每个扩展的编号、名称和类型名称，而无需导入载荷所在的 `.proto` 文件。

### `google.protobuf.Any` {#what-any}

[`google.protobuf.Any`](/reference/protobuf/google.protobuf#any) 是一个定义在 `google/protobuf/any.proto` 中的包装消息（wrapper message）：

```proto
syntax = "proto3";

package google.protobuf;

message Any {
  string type_url = 1;
  bytes value = 2;
}
```

不再通过扩展机制来扩展容器消息，而是让容器声明一个类型为 `google.protobuf.Any` 的字段。把消息打包进 `Any` 会将内部消息序列化（serialization）到 `value` 中，并把一个包含内部消息完全限定名（fully qualified name）的 URI 写入 `type_url`：

```cpp
media::UserContent content;
kittens::Video video;
video.set_title("Cute kittens");
content.mutable_payload()->PackFrom(video);

if (content.payload().Is<kittens::Video>()) {
  kittens::Video unpacked;
  if (content.payload().UnpackTo(&unpacked)) {
    // 使用解包后的消息
  }
}
```

## proto3 为何用 `Any` 取代了扩展 {#why-introduced}

在 proto2 中，扩展存在两个实际的问题：

1.  在不导入扩展的前提下，没有内置的方法来协调容器消息上的扩展编号。由于 `extend` 块位于单独的 `.proto` 文件中，两个团队可能在同一个共享容器消息上选中相同的字段编号，从而在线路上悄无声息地发生冲突。
2.  proto3 试图简化这门语言，让新的运行时（runtime）能够把消息表示为普通的[开放式结构体（open struct）](/design-decisions/opaque-apis)，只需最少的运行时机制。而扩展则要求有 `ExtensionRegistry`、消息上的扩展存储，以及每种语言中的参数化访问器（accessor）API。

`Any` 则同时避免了这两个问题：在二进制线路上，它只是一个带有 `string` 字段和 `bytes` 字段的普通消息；它的判别依据是全局唯一的消息名称，而不是经过协调的字段编号；而且运行时支持可以仅限于 `PackFrom` / `UnpackTo` 辅助方法，再加上 [ProtoJSON](/programming-guides/json#any) 和 TextFormat 中的特殊处理。

开放式结构体这一前提后来被放弃了（参见[我们更青睐 Opaque API](/design-decisions/opaque-apis)）。

扩展编号冲突的风险对扩展来说依然存在，但在大多数情况下可以通过使用[扩展声明](/programming-guides/extension_declarations)来缓解。

## 为什么我们后悔用 `Any` 来取代扩展 {#flaws}

### 二进制线路上的类型名称阻碍重命名与重新分包 {#type-url-lock-in}

Protobuf 二进制线路格式（wire format）的一个核心特性是：消息名称、字段名称和包名称都不会出现在线路上。由于二进制格式通过数字标签（tag）来标识字段，你可以重命名字段、重命名消息，或者把消息移动到另一个 `.proto` 包，而不会破坏与已部署二进制程序或已存储数据之间的线路兼容性。

`Any` 破坏了这一特性。由于 `PackFrom()` 在二进制线路上会把完全限定的消息名称写入 `type_url`，**任何被打包进 `Any` 的消息都无法安全地重命名或移动到另一个 `.proto` 包**：

*   如果消息被重命名或移动到新的包，`Is<T>()` 和 `UnpackTo()` 会把新描述符（descriptor）的 `full_name()` 与旧的 `type_url` 字符串进行比较，并拒绝已有的载荷，即使 `value` 中已序列化的字节在线路格式上是兼容的。
*   与此同时，新的二进制程序开始写入新的 `type_url` 字符串，而旧的二进制程序和回滚目标无法识别它。

更糟的是，**`Any` 并不是选择加入（opt-in）式的**。消息作者并不会声明自己的消息可能被打包进 `Any`。其他仓库或服务中的任何调用者都可以在消息所有者不知情的情况下把任意消息传给 `PackFrom()`；而且由于打包可能经由通用代码路径或反射（reflection）式代码路径发生，静态分析无法证明某个消息类型永远不会被存入 `Any`。这个属性十分诡异，让人难以判断重命名消息到底是否安全。

扩展与常规字段一样，通过数字标签在线路上标识字段。重命名扩展、重命名它所持有的消息类型，或者把二者移动到其他 `.proto` 包，在二进制线路上都是安全的。

### 与常规字段的线路格式不兼容 {#wire-incompatibility}

扩展的二进制线路编码与具有相同字段编号、类型和基数的常规字段完全一致。这使得常规字段与扩展之间的边界是可逆的：

*   如果容器消息上的某个常规字段造成了不必要的构建依赖，可以在不改变线路上任何一个字节的情况下，把它移出并放进一个具有相同字段编号和类型的 `extend` 块中。
*   反过来，一个被广泛使用的扩展也可以直接提升为容器消息上的常规字段。

`Any` 把它的载荷包裹在一个包含 `type_url`（字段 1）和 `value`（字段 2）的子消息中。它与普通的子消息字段在线路格式上不兼容，因此字段无法在不破坏线路格式的情况下迁入或迁出 `Any`。

### 线路体积开销 {#wire-size}

线路上的扩展标签是一个把字段编号和线路类型（wire type）编码在一起的可变长度整数（varint）：字段编号不超过 2047 时为 2 字节，对于最大的合法字段编号至多 5 字节。

每个 `Any` 消息在线路上除了嵌套的长度前缀之外，还要携带完整的 `type.googleapis.com/package.MessageName` 字符串。一个典型的 `type_url` 会为每个实例增加 40 到 80 字节。对于小消息或 `repeated google.protobuf.Any` 字段，重复出现的 `type_url` 字符串所占的空间往往比载荷本身还大。

### 内存开销与立即序列化 {#serialization}

由于 `Any` 把载荷存储为 `bytes value` 字段，而不是消息树中的类型化子消息，在内存中操作 `Any` 既笨拙又昂贵：

*   `PackFrom()` 会立即把内部消息序列化到 `bytes` 缓冲区中，即使外层消息只在内存中传递也是如此。
*   在大多数语言（包括 C++、Go、Python 和开源版 Java）中，每次读取时调用 `UnpackTo()` 都会分配一个单独的消息对象，并从头解析 `value`，除非调用者自行维护一个单独的缓存。相比之下，扩展直接存储在父消息内部（在 C++ 中还与父消息共享 arena），因此读取 `GetExtension()` 只是一次指针查找。

一个常见的误解是：对于不关心载荷的中间代理来说，`Any` 更为廉价，因为在调用 `UnpackTo()` 之前 `value` 会一直保持未解析状态。扩展本来就具有这一特性：如果某个二进制程序没有链接或注册某个扩展，这些字节会以未解析的状态留在未知字段（unknown fields）集合中，并在序列化时原样转发。即使某个二进制程序*确实*链接了该扩展，支持惰性字段（lazy field）的运行时也会把对扩展的解析推迟到第一次调用 `GetExtension()` 时进行，然后就地缓存解析后的子消息。

### 被破坏的 `MergeFrom`、相等性与反射语义 {#semantics}

对 Protobuf 来说，`Any` 只是一个包含两个字段的消息（`string type_url = 1; bytes value = 2;`），而不是类型化的容器。标准的消息操作作用于这两个标量（scalar）字段，而不是作用于内部打包的消息：

#### `MergeFrom` {#merging}

当两个带有子消息扩展的消息通过 `MergeFrom()` 合并时，扩展的子消息会按字段递归地合并，同一容器上不同的扩展也能共存。

当两个 `Any` 消息合并时，`MergeFrom()` 会把 `type_url` 和 `value` 当作普通的标量字段来合并，直接覆盖 `value`，而不是合并内部消息。更糟的是，由于 `google/protobuf/any.proto` 是用 `syntax = "proto3"` 定义的，`type_url` 和 `value` 都具有[隐式存在性（implicit presence）](/design-decisions/implicit-presence#merging)：

1.  假设 `A` 是一个打包了非空 `Bar` 消息的 `Any`（`type_url = "type.googleapis.com/Bar"`，`value = "\x08\x01"`）。
2.  假设 `B` 是一个打包了默认空 `Quux` 消息的 `Any`。由于全默认的消息会序列化为 0 字节，`B` 的 `type_url = "type.googleapis.com/Quux"`，`value = ""`。
3.  调用 `A.MergeFrom(B)` 会用 `"type.googleapis.com/Quux"` 覆盖 `A.type_url`，但由于 `B.value` 为空（`""`），隐式存在性会把 `B.value` 视为未设置，因而不会覆盖 `A.value`。

合并后的 `Any` 现在把 `Quux` 的 `type_url` 与 `Bar` 序列化后的线路字节配在了一起。

#### 相等性 {#equality}

对 `Any` 进行的标准消息相等性比较的是原始的 `value` 字节串，而不是逻辑上的内部消息。正如[序列化并非规范化](/programming-guides/serialization-not-canonical)一文所解释的，两个逻辑上相等的 Protobuf 消息可能序列化为不同的字节序列（例如由于映射条目（map entry）的顺序或未知字段），导致持有等价载荷的两个 `Any` 消息在比较时并不相等。

#### 反射与通用遍历 {#reflection}

除非工具链接了被打包消息的描述符，并编写了自定义的 `Any` 解包代码，否则反射遍历器、字段路径工具和脱敏（redaction）处理只能看到一个 `string type_url` 和一个不透明的 `bytes value`。扩展则拥有正常的 `FieldDescriptor` 条目，无需任何特殊处理即可被标准的反射遍历器访问到。

### 不适合移动端与 Lite 运行时 {#lite}

在移动端、嵌入式和 Web 客户端构建（`LITE_RUNTIME`）中，Protobuf 会剥离描述符和符号名称，以减小二进制体积，并避免在随客户端发布的二进制文件中泄露尚未发布的特性名称。

`Any` 依赖运行时类型名称来构造和校验 `type_url`：

*   在 **JavaLite** 中，`MessageLite` 不携带描述符名称，因此生成的 `Any` 类中干脆省略了 `Any.pack()`、`Any.unpack()` 和 `Any.is()`。调用者必须手工构造并比较 `type_url` 字符串。
*   在 **C++ Lite** 中，`Any::PackFrom<T>()` 和 `UnpackTo<T>()` 之所以能够工作，是因为代码生成器（code generator）会在每个消息类上生成一个 `FullMessageName()` 字符串字面量，这迫使二进制文件为与 `Any` 搭配使用的每一种类型都保留 `.proto` 包名和消息名。

扩展使用数字标签和生成的扩展标识符，它们在 `LITE_RUNTIME` 构建中可以工作，并且无需保留描述符字符串即可支持 tree shaking。

### 类型 URL 不提供动态模式发现 {#type-urls}

`type_url` 字段最初被格式化为 URL（`type.googleapis.com/...`），其设想是运行时或许会在解析时通过 HTTP 获取未知的模式。Protobuf 从未实现过远程类型获取，并且在 `any.proto` 中明确警告不要联络 `type_url` 端点，因为这会带来安全问题。每个解析器都只是简单地截掉最后一个 `/` 之前的所有内容；而在 JSON、TextFormat 或反射中解包 `Any` 仍然要求目标描述符已被链接或加载到本地二进制程序的描述符池（descriptor pool）中，这一点与扩展并无不同。

## 应该改用什么 {#instead}

### 常规子消息字段或 `oneof` {#oneof}

当可能的载荷类型集合是有界的、为容器作者所知，并且把它们直接导入容器 `.proto` 不会造成依赖问题时，请使用常规子消息字段或 `oneof`。`oneof` 把备选类型的集合显式地集中在一处声明，并且在每种语言中都能生成最整洁的 API。

### 配合扩展声明使用扩展 {#use-extensions}

当载荷定义需要放在单独的 `.proto` 文件中、以免容器依赖它们时，请使用[扩展](/programming-guides/editions#extensions)：

*   在容器的 `extensions` 区间上添加[扩展声明](/programming-guides/extension_declarations)，这样所有已分配的扩展编号和类型名称都会集中列在一处，并由 `protoc` 进行检查，而无需导入载荷所在的 `.proto` 文件。
*   如果对容器 `.proto` 文件的集中式代码审查所有权会成为添加扩展的团队的瓶颈，可以把可扩展的容器（或专用的扩展承载子消息）放入一个所有权更宽泛的单独 `.proto` 文件中。
*   如果你的容器消息目前位于 `syntax = "proto3"` 文件中（这类文件不允许使用 `extensions` 区间），请把该文件迁移到 [Protobuf 版次](/editions/overview)。把文件从 `proto3` 迁移到 2023 版次在线路格式上是兼容的，其余的 `proto3` 文件仍可导入它。

### `Any` 仍然适用的场景 {#when-any}

`Any` 仍然是正确工具的唯一场景是**无界的横向基础设施**：跨独立领域传输、记录或存储完全任意消息的系统（例如，像 `google.rpc.Status.details` 这样的通用远程过程调用（RPC）错误详情列表、通用的任务队列载荷，或死信队列），在这类系统中，为生态系统中的每一种消息类型都在信封上声明一个扩展并不现实。

每当你确实要使用 `Any` 时，请把每个被打包消息的包名和消息名当作你的线路协议中永久冻结的一部分。
