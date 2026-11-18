+++
title = "Rust Proto 设计决策"
weight = 785
linkTitle = "设计决策"
description = "解释 Rust Proto 实现做出的一些设计选择。"
type = "docs"
source_url = "https://protobuf.dev/reference/rust/rust-design-decisions/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

与任何库一样，Rust Protobuf 的设计同时考虑了 Google 第一方对 Rust 的使用需求与外部用户的需求。在这一设计空间中选定一条路径，意味着所做的某些选择在某些情况下对某些用户并非最优，即使从实现整体来看它是正确的选择。

本页介绍 Rust Protobuf 实现做出的一些较大的设计决策，以及促成这些决策的考量因素。

## 设计为“依托”（backed）其他 Protobuf 实现（包括 C++ Protobuf） {#backed-by-cpp}

Protobuf Rust 并不是 Protobuf 的纯 Rust 实现，而是构建在既有 Protobuf 实现之上的安全 Rust API——我们将这些实现称为内核（kernel）。

做出这一决定的最大考量因素，是让 Rust 能够以零开销（zero-cost）的方式加入一个已经在使用非 Rust Protobuf 的既有二进制程序。通过让该实现与 C++ Protobuf 生成代码（generated code）保持 ABI 兼容，就可以跨越语言边界（FFI）以普通指针的形式共享 Protobuf 消息（message），从而避免在一种语言中序列化（serialize）、把字节数组跨边界传递、再在另一种语言中反序列化（deserialize）的过程。这还能减小这些用例的二进制体积，因为避免了在二进制中为同样的消息按每种语言各嵌入一份冗余的模式（schema）信息。

Google 将 Rust 视为一个机会，可以渐进地为既有存量（brownfield）C++ 服务器的关键部分带来内存安全；而语言边界处的序列化开销会阻碍在这些重要且性能敏感的场景中用 Rust 替代 C++。如果我们追求的是一个不具备这种支持的全新（greenfield）Rust Protobuf 实现，最终只会阻碍 Rust 的采用，并迫使这些重要场景继续停留在 C++ 上。

Protobuf Rust 目前支持三种内核：

*   C++ 内核 - 生成代码依托 C++ Protobuf（“完整”实现，通常用于服务器）。该内核提供与使用 C++ 运行时（runtime）的 C++ 代码进行内存中互操作的能力。这是 Google 内部服务器的默认选择。
*   C++ Lite 内核 - 生成代码依托 C++ Lite Protobuf（通常用于移动端）。该内核提供与使用 C++ Lite 运行时的 C++ 代码进行内存中互操作的能力。这是 Google 内部移动应用的默认选择。
*   upb 内核 - 生成代码依托 [upb](https://github.com/protocolbuffers/protobuf/tree/main/upb)，一个用 C 编写、性能极高且二进制体积很小的 Protobuf 库。upb 的设计定位是作为其他语言 Protobuf 运行时的实现细节。这是开源构建中的默认选择，因为我们预计在这类构建中，与已经在使用 C++ Protobuf 的代码进行静态链接的情况会更少见。

Rust Protobuf 的设计支持多种备选实现（包括多种不同的内存布局），同时暴露完全相同的 API，使同一份应用代码可以重新编译为依托另一种实现。这一设计约束深刻影响着我们的公开 API 决策，包括访问器（getter）所使用的类型（本文后文会讨论）。

### 没有纯 Rust 内核 {#no-pure-rust}

既然我们把 API 设计为可由多种底层实现来支撑，一个自然的问题是：为什么目前受支持的内核全部是用 C 和 C++ 这两种内存不安全语言编写的。

虽然 Rust 作为内存安全语言能显著降低暴露于严重安全问题的风险，但没有任何语言能对安全问题免疫。我们作为内核支持的这些 Protobuf 实现已经过严格审查和模糊测试（fuzzing），其程度足以让 Google 放心在自己的服务器和应用中用它们对不可信输入执行无沙箱解析。

此时若用 Rust 从零编写一个全新的二进制解析器，人们普遍会认为它比我们既有的 C++ Protobuf 或 upb 解析器更容易包含严重漏洞——后者经过了广泛的模糊测试、测试与审查。

从长期看，支持纯 Rust 内核实现存在正当的理由，例如让开发者在构建时无需准备 Clang 来编译 C 代码。

我们预计 Google 将来会在某个时间点支持一个暴露相同 API 的纯 Rust 实现，但目前还没有具体路线图。我们也不计划再推出第二个官方 Rust Protobuf 实现——即通过规避依托 C++ Proto 与 upb 所带来的约束、从而拥有“更好”API 的实现——因为我们不希望割裂 Google 自身的 Protobuf 使用。

## View/Mut 代理类型 {#view-mut-proxy-types}

Rust Proto API 采用不透明的“代理（Proxy）”类型设计。对于一个定义了 `message SomeMsg {}` 的 `.proto` 文件，我们会生成 Rust 类型 `SomeMsg`、`SomeMsgView<'_>` 和 `SomeMsgMut<'_>`。一条简单的经验法则是：我们期望在默认情况下，View 与 Mut 类型在所有用法中分别代替 `&SomeMsg` 和 `&mut SomeMsg`，同时仍然具备你对这些类型所期望的全部借用检查（borrow checking）/Send 等行为。

### 理解这些类型的另一种视角 {#another-lens}

为了更好地理解这些类型的细微差别，不妨按如下方式来思考它们：

```rust
struct SomeMsg(Box<cpp::SomeMsg>);
struct SomeMsgView<'a>(&'a cpp::SomeMsg);
struct SomeMsgMut<'a>(&'a mut cpp::SomeMsg);
```

在这一视角下可以看到：

-   给定一个 `&SomeMsg`，可以获得一个 `SomeMsgView`（类似于给定 `&Box<T>` 可以得到 `&T`）。
-   给定一个 `SomeMsgView`，则*无法*获得 `&SomeMsg`（类似于给定 `&T` 却无法得到 `&Box<T>`）。

正如 `&Box` 的例子一样，这意味着在函数参数上，通常更好的做法是默认使用 `SomeMsgView<'a>` 而非 `&'a SomeMsg`，因为它允许超集范围的调用者使用该函数。

### 为什么 {#why}

这一设计主要有两个原因：解锁潜在的优化收益，以及它是内核设计的固有结果。

#### 优化机会带来的收益 {#optimization}

Protobuf 作为一项如此核心且广泛使用的技术，出现了一种不寻常的双重现象：一方面，它所有可能被观察到的行为几乎都会被某些人依赖；另一方面，相对较小的优化在规模化场景下也会产生异乎寻常的重大净影响。我们发现，类型越不透明，带来的杠杆效应就越高：它们让我们能够更审慎地决定究竟暴露哪些行为，也为我们优化实现留出了更大的空间。

`SomeMsgMut<'_>` 提供了 `&mut SomeMsg` 无法提供的机会：即我们可以惰性地构造它们，并且其实现细节可以不同于拥有所有权（owned）的消息表示形式。它还从本质上让我们能够控制某些原本无法限制或掌控的行为：例如，任何 `&mut` 都可以与 `std::mem::swap()` 搭配使用，而如果将 `&mut SomeChild` 交给调用者，这种行为会对父结构与子结构之间能够维持哪些不变量（invariant）施加严格的限制。

#### 内核设计的固有结果 {#kernel-design}

代理类型的另一个原因更多是我们内核设计的一种固有局限：当你持有一个 `&T` 时，内存中某处必须存在一个真实的 Rust `T`。

我们的 C++ 内核设计允许你解析一条包含嵌套消息（nested messages）的消息，并只为根消息创建一个小的 Rust 栈上分配（stack-allocated）对象，其余所有内存都存储在 C++ 堆上。当你之后访问某个子消息时，并不存在与该子消息对应的已分配 Rust 对象，因此那一刻没有可供借用的 Rust 实例。

通过使用代理类型，我们能够按需创建在语义上充当借用的 Rust 代理类型，而无需事先为这些实例预先分配（eagerly allocate）任何 Rust 内存。

## 非 std 类型 {#non-std}

### 可能与 std 类型直接对应的简单类型 {#corresponding-std}

在某些情况下，即使存在同名的对应 std 类型，Rust Protobuf API 也可能选择创建我们自己的类型，当前实现甚至可能只是对该 std 类型的简单包装，例如 `protobuf::UTF8Error`。

使用这些类型而非 std 类型，为我们在未来优化实现提供了更大的灵活性。虽然我们当前的实现使用的是 Rust 标准库的 UTF-8 校验，但通过创建我们自己的 `protobuf::Utf8Error` 类型，我们得以把实现改为使用 C++ Protobuf 中那个高度优化的 C++ UTF-8 校验实现，它比 Rust 标准库的 UTF-8 校验更快。

### ProtoString {#proto-string}

Rust 的 `str` 与 `std::string::String` 类型维持着严格的不变量：它们只包含有效的 UTF-8；但 C++ 的 `std::string` 类型并不强制任何此类保证。`string` 类型的 Protobuf 字段（field）的预期是只包含有效的 UTF-8，C++ Protobuf 也确实使用了一个正确且高度优化的 UTF8 校验器。然而，C++ Protobuf 的 API 表面并未被设计为把“其 `string` 字段始终包含有效 UTF-8”作为运行时不变量来严格强制；相反，在某些情况下它允许向 `string` 字段写入非 UTF8 数据，校验只会在稍后序列化发生时才进行。

为了让 Rust 能够集成进使用 C++ Protobuf 的既有代码库，同时实现零开销的边界跨越、且在 Rust 侧没有未定义行为（undefined behavior）的风险，我们不得不在 `string` 字段的访问器中避免使用 `str`/`String` 类型。作为替代，使用的是 `ProtoStr` 与 `ProtoString` 类型——它们分别是与 `str` 和 `String` 等价的类型，区别只是在极少数情况下可能包含无效的 UTF-8。这些类型让应用代码可以自行选择：是按需执行校验、以 `Result<&str>` 的形式观察字段，还是直接操作原始字节以避免任何运行时校验。所有设置器（setter）路径仍然设计为允许你传入 `&str` 或 `String` 类型。

我们清楚像 `str` 这样的基础词汇类型（vocabulary types）对惯用写法非常重要，并打算随着 Rust 使用细节的演进，持续关注这一决定是否正确。
