+++
title = "不支持可空 setter/getter"
weight = 89
description = "阐述 Protobuf 为何不支持可空 setter 与 getter"
type = "docs"
aliases = "/programming-guides/nullable-getters-setters/"
source_url = "https://protobuf.dev/design-decisions/nullable-getters-setters/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

我们收到过反馈，有些用户希望 protobuf 能在他们所选用的对 null 友好的语言（尤其是 Kotlin、C# 和 Rust）中支持可空 getter（读取器）/setter（设置器）。对于使用这些语言的用户来说，这看起来确实是一个有帮助的特性（feature），但这一设计选择存在种种权衡，Protobuf 团队最终因此决定不实现它们。

显式存在性（explicit presence）并不是一个与传统的可空性（nullability）观念直接对应的概念。个中差别颇为微妙，但显式存在性的设计哲学更接近于：“字段并非可空，但你可以检测字段是否被显式赋过值。正常访问时，若字段未被赋值，看到的会是某个默认值；而在需要时，你可以检查该字段是否曾被主动写入。”

不采用可空字段的最大原因，在于 `.proto` 文件中所指定默认值（default value）的预期行为。按设计，对一个未设置的字段调用 getter，返回的将是该字段的默认值。

**注意：** C# 确实会把*消息（message）*字段当作可空字段处理。这种与其他语言的不一致源于缺少不可变消息，因而无法创建可供共享的不可变默认实例。由于消息字段本来就不能指定默认值，所以这种做法在功能上并无问题。

举个例子，看看这个 `.proto` 文件：

```proto
message Msg { Child child = 1; }
message Child { Grandchild grandchild = 1; }
message Grandchild { int32 foo = 1 [default = 72]; }
```

以及对应的 Kotlin getter：

```kotlin
// 在我们的 API 中，getter 始终不可空：
msg.child.grandchild.foo == 72

// 若子消息可空，?. 运算符将取不到默认值：
msg?.child?.grandchild?.foo == null

// 或者在调用点冗余地复制一遍默认值：
(msg?.child?.grandchild?.foo ?: 72)
```

以及对应的 Rust getter：

```rust
// 在我们的 API 中：
msg.child().grandchild().foo()   // == 72

// 若每个 getter 都是 Option<T>，则写法冗长且观察不到默认值
msg.child().map(|c| c.grandchild()).map(|gc| gc.foo()) // == Option::None

// 对于少数需要同时观察字段的存在性与值的情形，还可以在这里使用
// 返回自定义 Optional 类型的 _opt() 访问器（Optional 类型与 Option
// 相似，但它还能感知默认值）：
msg.child().grandchild().foo_opt() // Optional::Unset(72)
```

如果存在可空 getter，它就必然要忽略用户指定的默认值（转而返回 null），这会导致令人意外且不一致的行为。可空 getter 的使用者如果想要访问字段的默认值，就得自己编写定制逻辑，在返回 null 时改用默认值——这也就抹去了可空 getter 本应带来的“代码更整洁、更简单”的好处。

同样，我们也不提供可空 setter，因为其行为会不符合直觉。先执行设置再执行读取，得到的值并不总是相同；而且调用设置操作时，也只有部分情况下才会影响该字段的 has-bit。

请注意，消息类型的字段始终是显式存在性字段（带有 hazzer，即用于设置 hasbit 的内联辅助方法）。proto3 默认让标量（scalar）字段采用隐式存在性（implicit presence，即不含 hazzer），除非将其显式标记为 `optional`；而 proto2 不支持隐式存在性。在[版次（Editions）](/editions/features#field_presence)中，除非使用了隐式存在性特性，显式存在性就是默认行为。鉴于预期今后几乎所有字段都将采用显式存在性，可空 getter 所带来的易用性（ergonomics）问题，预计会比当初在 proto3 用户那里更为突出。

由于这些问题，可空 setter/getter 将从根本上改变默认值的使用方式。尽管我们理解它可能带来的用处，但我们认为，它所引入的不一致性和困难并不值得。
