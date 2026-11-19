

+++
title = "插入点与通用服务：令人遗憾并已弃用"
weight = 92
description = "阐述 Protobuf 团队为何对插入点与通用服务感到遗憾，以及应当采用的替代做法"
type = "docs"
source_url = "https://protobuf.dev/design-decisions/insertion-points-and-generic-services/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

在 Protobuf 的早期历史（约 2008-2010 年）中，Protobuf 添加了两种不同的机制，允许 Protobuf 之外的代码把自己嫁接到 Protobuf 的生成代码（generated code）上：

*   **通用服务（generic services）**自首次公开发布起就已存在，是抽象的、与远程过程调用（RPC）系统无关的 `Service`、`Stub`、`RpcChannel` 和 `RpcController` 类，曾在 C++、Java 和 Python 生成器中得到支持
*   **插入点（insertion point）**于 2010 年加入，是生成器留在其输出中的注释标记，目的是让*第二个* protoc 插件（plugin）能够把任意文本拼接到生成文件的中部，包括拼接进生成的消息（message）类的类体之中

这两者是相互关联的：插入点与"弃用通用服务、改用 RPC 专属插件"出现在同一个发布版本中，而且插入点正是让一个独立的插件能够把自己的存根（stub）放回通用服务原先占用的同一个生成文件的机制之一。

通用服务自 2010 年起就被标记为弃用（deprecated），而插入点则一直被标注为"实验性"特性；不过，两者存续超过 15 年这一事实，可能错误地传递出它们仍持续稳定的信号。

两者都是 Protobuf 团队感到遗憾的设计决策：

*   通用服务自 2010 年起就被正式弃用，2010 年之后没有任何受支持的语言再添加它们。我们正致力于在未来的一个破坏性发布版本中最终关停这一行为。
*   插入点一直被标记为"EXPERIMENTAL"，并且在最初引入它们的生成器中至今仍然有效，但我们认为这一机制是个错误。新的语言实现不会输出插入点，我们也不建议新的插件使用插入点；而且我们清楚，对我们生成代码的私有实现细节做例行改动，就可能破坏使用插入点的用户。

我们对两者的建议相同：遵循 gRPC 所采用的模型——编写一个独立的插件，让它输出自己的文件，并为你的系统设计其 API；然后在它自己的构建目标中编译这些文件，该构建目标依赖于位于单独文件中的 Protobuf 生成代码。

## 共同的错误 {#shared-mistake}

这两个特性看起来不同，但因同一个原因而失败：它们都让 Protobuf 团队并不拥有的代码去依赖 Protobuf 生成代码的*内部*，而不是与其公开接口面组合。

正如[我们更青睐 Opaque API](/design-decisions/opaque-apis)一文所解释的，几乎所有东西都依赖 Protobuf，因此生成代码中每一个可观察到的细节都会被某些人依赖。让 Protobuf 得以持续演进的唯一办法，是审慎界定哪些细节属于 API、哪些属于实现。生成代码与运行时（runtime）一同按版本发布，并且*不是* API：为了让解析更快、消息更小、新特性成为可能，我们会自由地重构它（参见[跨版本运行时保证](/support/cross-version-runtime-guarantee)）。

插入点把一种依赖上述生成代码文本的途径交到第三方手里；通用服务则把一种 RPC 抽象固化进消息代码和核心运行时。无论哪种方式，生成代码的下一次改进都必须与 Protobuf 团队从未见过的代码"谈判"。

我们知道替代方案会让你付出什么代价。插入点给了你一次导入，以及一些看起来就像是消息自身方法的方法；通用服务让你无需编写插件就能得到一个与 RPC 无关的接口。放弃这些意味着多一次导入、多一个构建目标，而且如果你没有在使用 gRPC 这类现成的 RPC 系统，还意味着要自己编写一个插件。这份代价小、明确，且由插件作者一次性付清。而嫁接到生成代码上的代价则大、隐蔽，且由消息库下游的每一个人支付——每当生成代码变更时都要再付一次。

## 插入点 {#insertion-points}

### 插入点是什么 {#insertion-points-what}

C++、Java、Python 和 Objective-C 生成器会把注释标记写入其输出。一个 C++ 头文件大致如下所示：

```cpp
// @@protoc_insertion_point(includes)

namespace foo {

class Bar final : public ::google::protobuf::Message {
 public:
  // ...
  // @@protoc_insertion_point(class_scope:foo.Bar)
};

inline int32_t Bar::id() const {
  // @@protoc_insertion_point(field_get:foo.Bar.id)
  return _internal_id();
}

// @@protoc_insertion_point(namespace_scope)
}  // namespace foo

// @@protoc_insertion_point(global_scope)
```

在同一次 `protoc` 调用中稍后运行的插件可以返回一个 `CodeGeneratorResponse.File`，其 `insertion_point` 字段指明上述某个标记。随后 `protoc` 会把插件的文本拼接进文件，位置就在标记行的正上方，并继承该行的缩进。插件自始至终看不到它所编辑的文件；它只知道文件中某个位置的名称。

每个生成器都暴露自己临时设计的标记集合：C++ 有 `includes`、`namespace_scope`、`global_scope`、`class_scope:T`，以及每个生成的访问器（accessor）函数体内都有的一个标记；Java 有 `outer_class_scope`、`class_scope:T`、`builder_scope:T`、`enum_scope:T`，甚至还有 `message_implements:T` 和 `builder_implements:T`——它们让插件可以向生成类的 `implements` 子句添加任意接口；Python 则有 `imports`、`module_scope` 和 `class_scope:T`。

支撑这一切的插件端 API `GeneratorContext::OpenForInsert()`，自 2010 年引入以来一直带着这样一句注释："WARNING: This feature is currently EXPERIMENTAL and is subject to change"（警告：此特性目前处于实验阶段，随时可能变更）。它从未摆脱过这一状态。

### 它们为何侵入性过强 {#insertion-points-why}

**被插入的代码能看到实现细节，而没有任何东西阻止它使用这些细节。** 拼接进 `class_scope` 的文本会作为生成类的成员参与编译。它能看到私有字段（field）、内部辅助函数、基类、碰巧定义了的宏、碰巧被包含的头文件，以及一切声明的先后顺序。我们的文档一直写着"不要生成依赖标准代码生成器所声明的私有类成员的代码"，但这一机制无法强制执行该要求，插入者也无法声明它实际依赖的是什么。在实践中，Hyrum 定律（Hyrum's Law）应验：凡是可见的，就会被使用。

**随着运行时的演进，它们不可避免地会损坏。** Protobuf 的生成代码并非凝固不变；它是随其所属运行时一同发布、不断变动的实现细节。多年来，我们把 C++ 字段存储移进了内部的 `Impl_` 结构体，把很少被设置的字段从主对象中拆分出去，改变了存在性位（presence bit）的追踪方式，引入了 `_internal_` 访问器，增加了 arena 支持，更换了默认的头文件和宏，而且我们会继续这样做。每一次这样的改动，都是别人插入文本中一个潜在的编译错误。更糟的是，被插入的文本可能在继续通过编译的同时悄然违反新的不变量：直接写入字段却不设置其 hasbit 的代码，或读取现在采用惰性解析的子消息字段的代码，都以任何编译器都不会报告的方式出错。这些故障会在另一个团队的插件里、另一个代码仓库里、在不可预测的时间点浮现，而 Protobuf 团队无法预见它们，因为这种依赖针对的是*文本文件中的某个位置*，而不是某个已声明的 API。

**它们把不相干的代码熔接进同一个产物和同一个构建目标。** 被插入的代码与消息同处一个 `.pb.h`、`Foo.java` 或 `_pb2.py`，因此也同处一个库。所有依赖这些消息的人，现在都传递性地依赖插入插件所需要的一切——通常是一整套 RPC 运行时；而这个文件只有在一次 `protoc` 调用中按正确顺序运行每一个参与的插件才能生成。这就是为什么一个仅仅*定义*了服务的 `.proto` 文件，最终会迫使一个只用到消息的客户端去链接 RPC 技术栈；也是为什么消息库最终会在那些 RPC 技术栈不存在的平台上构建失败。

### 所有主要用户都已弃用插入点 {#insertion-points-history}

插入点唯一有分量的用途，是 RPC 系统把服务存根插入消息文件；而它们中的每一个，后来都转向了独立文件：

*   **gRPC C++** 一直生成独立的 `.grpc.pb.h` / `.grpc.pb.cc` 文件，并且在 `cc_generic_services` 启用时，其插件会拒绝运行。
*   **gRPC Python** 最初通过 `module_scope` 插入点把它的服务插入 `_pb2.py`。生成器现在默认写出独立的 `_pb2_grpc.py` 文件，而被插入的变体已被标记待移除（"THESE ELEMENTS WILL BE DEPRECATED. Please use the generated `*_pb2_grpc.py` files."——这些元素将被弃用，请改用生成的 `*_pb2_grpc.py` 文件）。
*   **gRPC Go** 曾经由 `protoc-gen-go` 内部的 `plugins=grpc` 选项生成，把服务输出到与消息相同的 `.pb.go` 文件中。该选项在 Go Protobuf 的 APIv2 重写中被移除；gRPC 现在自带 `protoc-gen-go-grpc`，由它写出 `_grpc.pb.go` 文件。

### 应当怎么做 {#insertion-points-instead}

请编写一个独立的插件，它：

*   输出自己的文件（`foo.grpc.pb.h`、`FooGrpc.java`、`foo_pb2_grpc.py`、`foo_grpc.pb.go` 等），并且从不指名任何 `insertion_point`；
*   只通过消息公开的生成 API，以及反射（reflection）、描述符（descriptor）和自定义选项（custom option）来依赖消息；而且
*   由它自己的构建规则（某个 `*_grpc_library` 或等价物）驱动，该构建规则依赖消息库，而不是隐藏在消息的构建过程之中。

如果你需要*看起来*就像是消息自身方法的针对每条消息的行为，请使用各语言已有的、用于扩展你所不拥有类型的惯用法：C++ 和 Rust 中的自由函数或 trait，Java 和 Kotlin 中的静态工具类或扩展函数，包装类型，等等。如果你需要针对每条消息的*数据*，请把它放进一个自定义选项，并在构建时或运行时通过描述符读取。

这同样适用于小幅度的插入。一个与 RPC 毫无关系的 `class_scope` 辅助代码不会把 RPC 运行时拖进消息库，但它仍会作为生成类的成员参与编译，仍能看到生成类的每一个私有细节，并且在那些细节变化时仍会损坏；[它们为何侵入性过强](#insertion-points-why)中的前两个问题并不取决于插入内容的大小。通过 `message_implements:T`、`builder_implements:T` 或 `interface_extends:T` 添加的接口没有一对一的替代物，而且这是有意为之：请使用适配器或包装类型，或者以描述符为键的注册表，而不是去改变一个你所不拥有的类的类型层级。

## 通用服务 {#generic-services}

### 通用服务是什么 {#generic-services-what}

通用服务源自 2008 年的最初设计，其构建理念是：RPC 系统可以通过实现 `RpcChannel` 和 `RpcController` 从底层接入。其意图是让 Protobuf 一次性定义服务的形态，而每一种 RPC 实现都使自己去适配这个形态。

### 它们为何是一次不充分的泛化 {#generic-services-why}

`service.h` 头文件把控制器描述为"我们期望所有实现都支持的一组'最小公分母'特性"。事实证明，这个最小公分母太小，装不下一个真正的 RPC 系统：

*   **仅支持一元调用。** `CallMethod(method, controller, request, response, done)` 恰好接收一个请求消息，并恰好产出一个响应消息。客户端流、服务端流和双向流——gRPC 与 Stubby 的一等特性——完全无法表达。
*   **只有一种硬编码的调用约定。** 该接口是异步的，带有一个 `Closure*` 完成回调（一个被暴露在公开接口中的 Google 专有类型）。它不适合阻塞调用、future、完成队列、协程、Kotlin 的 `suspend` 函数或响应式流。仅仅额外支持一种约定——Java 中的阻塞调用——就需要第二套并行的生成类型：`BlockingInterface`、`BlockingStub`、`BlockingRpcChannel`、`BlockingService` 和 `ServiceException`。
*   **没有容纳 RPC 语义的空间。** `RpcController` 只提供 `Failed()`、`ErrorText()`、`StartCancel()`、`SetFailed(string)`、`IsCanceled()` 和 `NotifyOnCancel()`，再无其他：没有截止时间，没有元数据或头部，没有结构化的状态码（错误只是一个字符串），没有压缩，没有认证上下文，没有拦截器，也没有流量控制。任何真实系统都必须把控制器向下转型为它自己的子类型才能拿到这些能力；到那一步，"通用"层不过是我们自己文档所说的，"比起为单一系统量身定制的代码，多了好几层间接"。
*   **要求完整的反射。** 分发经由 `MethodDescriptor` 和 `Message` 而非 `MessageLite` 进行，因此通用服务无法与移动和嵌入式平台上的 lite 运行时一同使用——而恰恰是在这些平台上，一个可移植的 RPC 方案才最有价值。`protoc` 会直接强制执行这一点："含有 `optimize_for = LITE_RUNTIME` 的文件不能定义服务，除非你把 `cc_generic_services` 和 `java_generic_services` 两个选项都设为 false。"
*   **它们把消息库与一种 RPC 抽象绑在了一起。** 服务代码被输出到与消息相同的文件里，而 `service.h` 则位于核心运行时中。这与插入点是同一类耦合问题，并带来同样的构建期后果。

结果是，几乎没有什么 RPC 系统构建在通用服务之上。gRPC 在每种语言中都生成自己的存根，而且一旦 `cc_generic_services` 开启，它的 C++ 插件就会直接失败。最初的设计目标——"一次性定义形态，让 RPC 系统自行适配"——在实践中被颠倒过来：通用形态几乎没有适配到任何用户，而 RPC 系统反而不得不围绕如何摆脱它来设计。

### 应当怎么做 {#generic-services-instead}

请遵循 gRPC 模型。把 `service` 定义保留在你的 `.proto` 文件中：它们仍然是 API 的权威模式（schema），可以通过反射和描述符访问，并且可以携带自定义选项。但服务的*代码*应当来自 RPC 系统自己的 protoc 插件，输出到它自己的文件中，其 API 为该系统的调用约定、流式模型、状态码、截止时间和元数据而设计。

Protobuf 的角色是充当接口定义语言和消息层。RPC 层属于 RPC 系统。

## 对新语言和新插件的指导 {#guidance}

*   新的 Protobuf 语言实现不会输出插入点，也不会生成通用服务。这不是一个日后会修复的疏忽。
*   新的 protoc 插件生成独立文件。一个需要钻进 Protobuf 生成代码"内部"的插件，表明该设计应当被重新审视，而不是添加插入点的理由。
*   对生成代码结构的变更如果破坏了插入在插入点处的代码，不会被视作对 Protobuf 的破坏性变更（breaking change）。
